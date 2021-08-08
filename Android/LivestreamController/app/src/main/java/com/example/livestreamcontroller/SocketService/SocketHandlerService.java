package com.example.livestreamcontroller.SocketService;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;

import androidx.annotation.RequiresApi;

import com.example.livestreamcontroller.SocketMessageHandler;
import com.example.livestreamcontroller.StreamEvents;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@RequiresApi(api = Build.VERSION_CODES.N)
public class SocketHandlerService extends Service implements SocketHandler.SocketFailureListener {

    private final IBinder binder = new SocketBinder();

    private String IPAddress = "10.0.0.209";
    private int socketAddress = 5000;

    private SocketHandler socket;
    private final StreamStates streamStates = new StreamStates();

    private Handler mainHandler;

    private boolean socketShouldBeOpen = false;
    ExecutorService executorService = Executors.newSingleThreadExecutor();

    public SocketHandlerService() {
        setupSocket();
    }
    public void closeSocket(){
        socket.closeSocket();
    }
    public boolean socketShouldBeOpen(){
        return socketShouldBeOpen;
    }
    public String getIPAddress(){
        return IPAddress;
    }
    public int getPort(){
        return socketAddress;
    }

    @Override
    public IBinder onBind(Intent intent){
        return binder;
    }

    public class SocketBinder extends Binder {
        public SocketHandlerService getService(){
            return SocketHandlerService.this;
        }
    }

    public void setNewAddress(String IPAddress, int port){
        this.IPAddress = IPAddress;
        socketAddress = port;
        if (!socket.isClosed()){
            socket.closeSocket();
        }
        setupSocket();
    }

    public StreamStates getStreamStates(){
        return streamStates;
    }
    public void setHandler(Handler handler){
        mainHandler = handler;
        streamStates.setCallbackThread(handler);
    }

    public void sendData(String data) {
        socket.sendData(data, executorService);
    }

    private void setupSocket(){
        System.out.println("Attempting to create socket object");
        if (this.socket != null){
            this.socket.closeSocket();
            this.socket = null;
        }
        this.socket = new SocketHandler(IPAddress, socketAddress, messageHandler, true);
        socket.setListener(this);

        Thread thread = new Thread(socket::startupSocket);

        socket.addOnConnect(this::updateAllStates);
        socket.addOnConnect(this::setShouldBeOpenTrue);
        socket.addOnConnect(this::updateStatuses);

        thread.start();
    }

    public void setShouldBeOpenTrue(){
        socketShouldBeOpen = true;
    }

    private Runnable doTheDialog;
    public void setDoTheDialog(Runnable runnable){
        doTheDialog = runnable;
    }

    private Runnable updateNetworkStatusesRunnable = null;
    public void setUpdateNetworkStatusesRunnable(Runnable runnable){
        updateNetworkStatusesRunnable = runnable;
    }

    public void updateStatuses(){
        if (updateNetworkStatusesRunnable != null){
            mainHandler.post(updateNetworkStatusesRunnable);
        }
    }

    public void onSocketSetupFailure(){
        System.out.println("Socket setup failure!!!!!");
        socketShouldBeOpen = false;
        updateStatuses();
        mainHandler.post(doTheDialog);
    }
    public void onSocketRuntimeFailure(){
        socketShouldBeOpen = false;
        updateStatuses();
        mainHandler.post(doTheDialog);
    }
    public void onSocketClose(){
        updateStatuses();
        socketShouldBeOpen = false;
    }


    public void updateAllStates(){
        socket.sendData("{\"type\":\"update\", \"specifier\":\"all\"}", executorService);
    }

    private final SocketMessageHandler messageHandler =
            message -> {
                try {
                    System.out.println("I shall handle thou message");
                    JSONObject reader = new JSONObject(message);
                    JSONArray names = reader.names();
                    if (names != null){
                        if (names.get(0).equals("states")){
                            JSONArray data = (JSONArray) reader.get("states");
                            String event = ((String) data.get(0)).toLowerCase();

                            switch (event) {
                                case "stream_running":
                                    streamStates.setValue(StreamEvents.STREAM_RUNNING,
                                            data.get(1).toString());
                                    break;
                                case "stream_is_setup":
                                    streamStates.setValue(StreamEvents.STREAM_IS_SETUP,
                                            data.get(1).toString());
                                    break;
                                case "stream_title":
                                    streamStates.setValue(StreamEvents.STREAM_TITLE,
                                            (String) data.get(1));
                                    break;
                                case "stream_is_muted":
                                    String value = data.get(1).toString();
                                    // Note that we are receiving 'if the stream is muted'
                                    // but are saving the value 'is stream on'
                                    // the incoming value needs to be inverted
                                    value = (value.equals("true")) ? "false" : "true";
                                    streamStates.setValue(StreamEvents.STREAM_SOUND_ON, value);
                                    break;
                                case "change_with_clicker":
                                    streamStates.setValue(StreamEvents.CHANGE_WITH_CLICKER,
                                            data.get(1).toString());
                                    break;
                                case "auto_change_to_camera":
                                    streamStates.setValue(StreamEvents.AUTO_CHANGE_TO_CAMERA,
                                            data.get(1).toString());
                                    break;
                                case "augmented":
                                    streamStates.setValue(StreamEvents.AUGMENTED,
                                            data.get(1).toString());
                                    break;
                                case "current_scene":
                                    streamStates.setValue(StreamEvents.CURRENT_SCENE, (String) data.get(1));
                                    break;
                                case "current_camera_sub_scene":
                                    streamStates.setValue(StreamEvents.CURRENT_CAMERA_SUB_SCENE,
                                            (String) data.get(1));
                                    break;
                                case "current_screen_sub_scene":
                                    streamStates.setValue(StreamEvents.CURRENT_SCREEN_SUB_SCENE,
                                            (String) data.get(1));
                                    break;
                                case "sound_on":
                                    streamStates.setValue(StreamEvents.COMPUTER_SOUND_ON,
                                            data.get(1).toString());
                                    break;
                                case "timer_not_running":
                                    streamStates.setValue(StreamEvents.TIMER_NOT_RUNNING,
                                            data.get(1).toString());
                                    break;
                                case "timer_text":
                                    streamStates.setValue(StreamEvents.TIMER_TEXT, data.get(1).toString());
                                    break;
                                case "timer_length":
                                    streamStates.setValue(StreamEvents.TIMER_LENGTH,
                                            data.get(1).toString());
                            }
                        }
                    }
                } catch (JSONException e){
                    System.out.println("Error loading JSON");
                }
                System.out.println("Received from Socket: " + message);
            };

}