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
        if (socketShouldBeOpen){
            updateStatuses();
        }
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
        socket.sendData("{\"type\":\"update\", \"update\":\"all\"}", executorService);
    }

    private final SocketMessageHandler messageHandler =
            message -> {
                try {
                    //need to change this to backwards compatible with the sending patterns
                    System.out.println("I shall handle thou message");
                    JSONObject reader = new JSONObject(message);
                    String names = (String) reader.get("type");
                    if (names.equals("update")){
                        {
                            String button = (String) reader.get("update");

                            switch (button) {
                                case "Stream_Running":
                                    streamStates.setValue(StreamEvents.STREAM_RUNNING,
                                            reader.get("data").toString());
                                    break;
                                case "Stream_Is_Setup":
                                    streamStates.setValue(StreamEvents.STREAM_IS_SETUP,
                                            reader.get("data").toString());
                                    break;
                                case "Stream_Title":
                                    streamStates.setValue(StreamEvents.STREAM_TITLE,
                                            reader.get("data").toString());
                                    break;
                                case "Stream_Is_Muted":
                                    String value = reader.get("data").toString();
                                    // Note that we are receiving 'if the stream is muted'
                                    // but are saving the value 'is stream on'
                                    // the incoming value needs to be inverted
                                    value = (value.equals("true")) ? "false" : "true";
                                    streamStates.setValue(StreamEvents.STREAM_SOUND_ON, value);
                                    break;
                                case "Change_With_Clicker":
                                    streamStates.setValue(StreamEvents.CHANGE_WITH_CLICKER,
                                            reader.get("data").toString());
                                    break;
                                case "Timer_Can_Run":
                                    streamStates.setValue(StreamEvents.TIMER_CAN_RUN,
                                            reader.get("data").toString());
                                    break;
                                case "Scene_Is_Augmented":
                                    streamStates.setValue(StreamEvents.SCENE_IS_AUGMENTED,
                                            reader.get("data").toString());
                                    break;
                                case "Scene":
                                    streamStates.setValue(StreamEvents.CURRENT_SCENE,
                                            reader.get("data").toString());
                                    break;
                                case "SubScene":
                                    String data = reader.get("data").toString();
                                    if (data.startsWith("Camera")){
                                        streamStates.setValue(StreamEvents.CURRENT_CAMERA_SUB_SCENE,
                                                data);
                                    } else if (data.startsWith("Screen")){
                                        streamStates.setValue(StreamEvents.CURRENT_SCREEN_SUB_SCENE,
                                                data);
                                    }
                                    break;
                                case "Computer_Sound_Is_On":
                                    streamStates.setValue(StreamEvents.COMPUTER_SOUND_ON,
                                            reader.get("data").toString());
                                    break;
                                case "Timer_Text":
                                    streamStates.setValue(StreamEvents.TIMER_TEXT,
                                            reader.get("data").toString());
                                    break;
                                case "Timer_Length":
                                    streamStates.setValue(StreamEvents.TIMER_LENGTH,
                                            reader.get("data").toString());
                            }
                        }
                    }
                } catch (JSONException e){
                    System.out.println("Error loading JSON");
                }
                System.out.println("Received from Socket: " + message);
            };

}