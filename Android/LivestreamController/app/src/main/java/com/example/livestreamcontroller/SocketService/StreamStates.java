package com.example.livestreamcontroller.SocketService;

import android.os.Build;
import android.os.Handler;

import androidx.annotation.RequiresApi;

import com.example.livestreamcontroller.StateChangeUiRunnable;
import com.example.livestreamcontroller.StreamEvents;

import java.util.HashMap;

@RequiresApi(api = Build.VERSION_CODES.N)
public class StreamStates {

    private final HashMap<StreamEvents, String> streamStates = new HashMap<>();
    private boolean hasCallback = false;
    private StateChangeUiRunnable callback;
    private Handler callbackThread;

    StreamStates(){
        streamStates.put(StreamEvents.STREAM_RUNNING, "false");
        streamStates.put(StreamEvents.STREAM_IS_SETUP, "false");
        streamStates.put(StreamEvents.STREAM_TITLE, "null");
        streamStates.put(StreamEvents.CHANGE_WITH_CLICKER, "false");
        streamStates.put(StreamEvents.TIMER_CAN_RUN, "true");
        streamStates.put(StreamEvents.CURRENT_SCENE, "camera");
        streamStates.put(StreamEvents.CURRENT_CAMERA_SUB_SCENE, "Camera_None");
        streamStates.put(StreamEvents.CURRENT_SCREEN_SUB_SCENE, "Screen_None");
        streamStates.put(StreamEvents.SCENE_IS_AUGMENTED, "false");
        streamStates.put(StreamEvents.TIMER_TEXT, "0.0");
        streamStates.put(StreamEvents.TIMER_LENGTH, "15");
        streamStates.put(StreamEvents.STREAM_SOUND_ON, "true");
        streamStates.put(StreamEvents.COMPUTER_SOUND_ON, "true");
    }

    public void setCallback(StateChangeUiRunnable runnable){
        this.callback = runnable;
        hasCallback = (runnable != null);
    }
    public void setCallbackThread(Handler handler){
        this.callbackThread = handler;
    }

    public void setValue(StreamEvents key, String newValue){
        if (!streamStates.containsKey(key)){
            throw new IllegalArgumentException("Key: " + key + "does not exist!");
        }
        streamStates.put(key, newValue);
        if (hasCallback)
            callbackThread.post(() -> callback.run(key, newValue));
    }

    public String get(StreamEvents key){
        if (!streamStates.containsKey(key)){
            throw new IllegalArgumentException();
        }
        return streamStates.get(key);
    }
}
