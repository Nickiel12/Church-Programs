package com.example.livestreamcontroller.SocketService;

import android.os.Build;

import androidx.annotation.RequiresApi;

import com.example.livestreamcontroller.SocketMessageHandler;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Scanner;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

@RequiresApi(api= Build.VERSION_CODES.KITKAT)
public class SocketHandler {

    private final String IPAddress;
    private final int socketPort;

    private Socket socket;
    private OutputStreamWriter socketOutStream;
    private BufferedReader socketInStream;
    private Scanner reader;

    private final ArrayList<Runnable> onConnectRunnables;
    private final SocketMessageHandler messageHandler;

    private final ScheduledExecutorService executorService;

    SocketFailureListener listener = null;

    public interface SocketFailureListener {
        void onSocketSetupFailure();
        void onSocketRuntimeFailure();
        void onSocketClose();
    }

    private boolean doListen;

    private boolean hasConnected = false;

    public SocketHandler(String targetIPAddress, int targetPort, SocketMessageHandler messageHandler) {
        this.IPAddress = targetIPAddress;
        this.socketPort = targetPort;
        this.messageHandler = messageHandler;
        executorService = Executors.newSingleThreadScheduledExecutor();

        doListen = false;
        onConnectRunnables = new ArrayList<>();

    }

    public SocketHandler(String targetIPAddress, int targetPort, SocketMessageHandler messageHandler,
                         boolean startListenerOnConnect){
        this(targetIPAddress, targetPort, messageHandler);
        this.addOnConnect(() -> this.setDoListen(startListenerOnConnect));
    }

    public void setListener(SocketFailureListener listener) {
        this.listener = listener;
    }

    public boolean isClosed(){return socket == null || socket.isClosed();}
    public boolean getDoListen(){return doListen;}
    public boolean getHasConnected(){return hasConnected;}

    public void addOnConnect(Runnable runnable){ onConnectRunnables.add(runnable); }
    public void removeOnConnect(Runnable runnable) { onConnectRunnables.remove(runnable); }

    public void setDoListen(boolean doListen){
        System.out.println("Setting doListen: " + doListen);
        this.doListen = doListen;
        if (doListen){
            executorService.schedule(this::listenToInput, 100, TimeUnit.MILLISECONDS);
        }
    }

    private int numberFalseReads = 0;
    private void listenToInput(){
        System.out.println("Socket Listener loop starting");
        if (numberFalseReads > 5){
            System.out.println("5 False socket reads, assuming the socket closed: Closing Socket");
            numberFalseReads = 0;
            setDoListen(false);

            listener.onSocketRuntimeFailure();
            closeSocket();
        }
        String next;
        if (reader.hasNext()){
            next = reader.nextLine();
            System.out.println("Received a message!:");
            System.out.println(next);

            this.messageHandler.run(next);

        } else {
            numberFalseReads++;
        }
        if (doListen) executorService.schedule(this::listenToInput, 100, TimeUnit.MILLISECONDS);
    }

    public void sendData(String data, ExecutorService execServ) {
        execServ.submit(() -> {
            try {
                socketOutStream.write(data);
                socketOutStream.flush();
                System.out.printf("Sent to socket: %s\n", data);
            } catch (IOException e) {
                closeSocket();
                listener.onSocketRuntimeFailure();
                e.printStackTrace();
            }
        });
    }

    private int numAttempts = 0;
    public void startupSocket() {
        System.out.println("Attempting to start socket");
        try {
            numAttempts += 1;
            if (numAttempts > 5){
                System.out.println("5 failed socket setups: assuming unreachable");
                listener.onSocketSetupFailure();
                numAttempts = 0;
                return;
            }
            SocketAddress address = new InetSocketAddress(IPAddress, socketPort);
            int timeoutMillis = 1000;

            socket = new Socket();
            socket.connect(address, timeoutMillis);
            socket.setKeepAlive(true);

            socketOutStream = new OutputStreamWriter(socket.getOutputStream(),
                    StandardCharsets.UTF_8);

            socketInStream = new BufferedReader(new InputStreamReader(
                    socket.getInputStream()));

            if (socket.isConnected()){
                System.out.println("Socket Connected");
                hasConnected = true;
            } else {
                System.out.println("Socket Not Connected! Please worry");
            }

            // Runs all of the onConnectRunnables when socket succeeds
            for (Runnable onConnectRunnable : onConnectRunnables) {
                new Thread(onConnectRunnable).start();
            }

            reader = new Scanner(socketInStream);

        } catch (UnknownHostException e) {
            System.out.println("Unknown host: " + IPAddress);
            listener.onSocketSetupFailure();

        } catch  (IOException e) {
            System.out.println(e.getMessage());
            startupSocket();
        }
    }

    public void closeSocket(){
        try {
            setDoListen(false);
            if (socket != null){
                socket.close();
            }
            hasConnected = false;
            listener.onSocketClose();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
