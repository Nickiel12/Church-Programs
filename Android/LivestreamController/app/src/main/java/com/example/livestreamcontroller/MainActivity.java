package com.example.livestreamcontroller;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.content.res.AppCompatResources;
import androidx.core.os.HandlerCompat;
import androidx.fragment.app.DialogFragment;
import androidx.lifecycle.Lifecycle;
import androidx.lifecycle.OnLifecycleEvent;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import android.animation.ArgbEvaluator;
import android.animation.ValueAnimator;
import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.provider.Settings;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;

import com.example.livestreamcontroller.SocketService.SocketAddressDialog;
import com.example.livestreamcontroller.SocketService.SocketErrorDialog;
import com.example.livestreamcontroller.SocketService.SocketHandlerService;
import com.example.livestreamcontroller.SocketService.StreamStates;
import com.google.android.material.snackbar.BaseTransientBottomBar;
import com.google.android.material.snackbar.Snackbar;
import com.google.android.material.switchmaterial.SwitchMaterial;

import java.util.HashMap;


@RequiresApi(api = Build.VERSION_CODES.N)
public class MainActivity extends AppCompatActivity implements SwipeRefreshLayout.OnRefreshListener,
                SocketAddressDialog.SocketDialogListener, SocketErrorDialog.SocketErrorDialogListener {

    Handler mainThreadHandler = HandlerCompat.createAsync(Looper.getMainLooper());
    SocketHandlerService socketService;
    boolean socketIsBound = false;
    StreamStates streamStates;

    ButtonHandler buttonHandler = new ButtonHandler(streamStates);

    HashMap<Integer, Integer> activeExtrasMap, inactiveExtrasMap, panelControlsMap;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        wireButtons();

        activeExtrasMap = new HashMap<>();
        activeExtrasMap.put(R.id.CameraNoneButton, R.drawable.camera_main_active);
        activeExtrasMap.put(R.id.CameraTopRightButton, R.drawable.camera_main_top_right_active);
        activeExtrasMap.put(R.id.CameraBottomLeftButton, R.drawable.camera_main_bottom_left_activepng);
        activeExtrasMap.put(R.id.CameraBottomRightButton, R.drawable.camera_main_bottom_right_active);
        activeExtrasMap.put(R.id.ScreenNoneButton, R.drawable.screen_main_active);
        activeExtrasMap.put(R.id.ScreenTopRightButton, R.drawable.screen_main_top_right_active);
        activeExtrasMap.put(R.id.ScreenBottomRightButton, R.drawable.screen_main_bottom_right_active);

        inactiveExtrasMap = new HashMap<>();
        inactiveExtrasMap.put(R.id.CameraNoneButton, R.drawable.camera_main);
        inactiveExtrasMap.put(R.id.CameraTopRightButton, R.drawable.camera_main_top_right);
        inactiveExtrasMap.put(R.id.CameraBottomLeftButton, R.drawable.camera_main_bottom_left);
        inactiveExtrasMap.put(R.id.CameraBottomRightButton, R.drawable.camera_main_bottom_right);
        inactiveExtrasMap.put(R.id.ScreenNoneButton, R.drawable.screen_main);
        inactiveExtrasMap.put(R.id.ScreenTopRightButton, R.drawable.screen_main_top_right);
        inactiveExtrasMap.put(R.id.ScreenBottomRightButton, R.drawable.screen_main_bottom_right);

        panelControlsMap = new HashMap<>();
        panelControlsMap.put(R.id.ShowHideTopPanel, R.id.ExtraButtonsTable);
        panelControlsMap.put(R.id.ShowHideTimerExtras, R.id.TimerTimeTable);
        panelControlsMap.put(R.id.ShowHideSlideControls, R.id.SlideButtonRow);
        panelControlsMap.put(R.id.ShowHideMediaControls, R.id.SoundControlRow);
        panelControlsMap.put(R.id.ShowHideRecordStreamPanel, R.id.RecordStreamBar);
    }

    @Override
    protected void onStart(){
        super.onStart();
        Intent intent = new Intent(this, SocketHandlerService.class);
        bindService(intent, connection,
                Context.BIND_AUTO_CREATE);
        ((SwipeRefreshLayout)findViewById(R.id.swiperefresh)).setOnRefreshListener(this);

        findViewById(R.id.ExtraButtonsTable).setVisibility(View.GONE);
        findViewById(R.id.TimerTimeTable).setVisibility(View.GONE);
        findViewById(R.id.SlideButtonRow).setVisibility(View.GONE);
        findViewById(R.id.SoundControlRow).setVisibility(View.GONE);

        updateStatuses();
    }

    public void onRefresh() {

        updateStatuses();

        System.out.println("*Slurp* Ahhh, Refreshing!");
        if (socketService.socketShouldBeOpen()){
            socketService.updateAllStates();
        } else {
            socketDialog();
        }
        ((SwipeRefreshLayout) findViewById(R.id.swiperefresh)).setRefreshing(false);
    }

    /**
     * Defines callbacks for service binding, passed to bindService()
     */
    private final ServiceConnection connection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName componentName, IBinder iBinder) {
            SocketHandlerService.SocketBinder binder = (SocketHandlerService.SocketBinder) iBinder;
            socketService = binder.getService();
            socketService.setHandler(mainThreadHandler);
            socketService.setDoTheDialog(MainActivity.this::socketDialog);
            socketService.setUpdateNetworkStatusesRunnable(MainActivity.this::updateStatuses);

            streamStates = socketService.getStreamStates();

            // TODO: Make sure this didn't break something
            streamStates.setCallback(MainActivity.this::updateVisualFromEvent);

            buttonHandler.setStreamStates(streamStates);
            socketIsBound = true;
        }

        @Override
        public void onServiceDisconnected(ComponentName componentName) {
            socketIsBound = false;
            System.out.println("Wahaaaa");
            buttonHandler.setStreamStates(null);
            streamStates = null;

        }
    };

    private int currentCameraScene = R.id.CameraNoneButton;
    private int currentScreenScene = R.id.ScreenNoneButton;

    private void updateVisualFromEvent(StreamEvents event, String eventValue){
        System.out.println("Processing " + event.toString() + " with value : " + eventValue);

        if (event == StreamEvents.CURRENT_SCENE){

            if (eventValue.equals("Scene_Camera")){
                findViewById(R.id.SetSceneCameraButton).setBackgroundColor(getColor(R.color.GREEN));
                findViewById(R.id.SetSceneScreenButton).setBackgroundColor(getColor(R.color.RED));
                ((SwitchMaterial) findViewById(R.id.AugmentSwitch)).setChecked(false);
            } else if (eventValue.equals("Scene_Screen")){
                findViewById(R.id.SetSceneScreenButton).setBackgroundColor(getColor(R.color.GREEN));
                findViewById(R.id.SetSceneCameraButton).setBackgroundColor(getColor(R.color.RED));
                ((SwitchMaterial) findViewById(R.id.AugmentSwitch)).setChecked(false);
            }
        }
         else if (event == StreamEvents.CURRENT_CAMERA_SUB_SCENE){
            switch(eventValue){
                case "Camera_None":
                    setExtraButtonHalo(R.id.CameraNoneButton, true);
                    currentCameraScene = R.id.CameraNoneButton;
                    break;
                case "Camera_Top_Right":
                    setExtraButtonHalo(R.id.CameraTopRightButton, true);
                    currentCameraScene = R.id.CameraTopRightButton;
                    break;
                case "Camera_Bottom_Right":
                    setExtraButtonHalo(R.id.CameraBottomRightButton, true);
                    currentCameraScene = R.id.CameraBottomRightButton;
                    break;
                case "Camera_Bottom_Left":
                    setExtraButtonHalo(R.id.CameraBottomLeftButton, true);
                    currentCameraScene = R.id.CameraBottomLeftButton;
                    break;
            }
        } else if (event == StreamEvents.CURRENT_SCREEN_SUB_SCENE){
            switch (eventValue){
                case "Screen_None":
                    setExtraButtonHalo(R.id.ScreenNoneButton, false);
                    currentScreenScene = R.id.ScreenNoneButton;
                    break;
                case "Screen_Top_Right":
                    setExtraButtonHalo(R.id.ScreenTopRightButton, false);
                    currentScreenScene = R.id.ScreenTopRightButton;
                    break;
                case "Screen_Bottom_Right":
                    setExtraButtonHalo(R.id.ScreenBottomRightButton, false);
                    currentScreenScene = R.id.ScreenBottomRightButton;
                    break;
            }
        } else
        switch (event) {
            case AUGMENTED:
                if (eventValue.equals("true")){
                    ((SwitchMaterial) findViewById(R.id.AugmentSwitch)).setChecked(true);
                    findViewById(R.id.SetSceneScreenButton).setBackgroundColor(getColor(R.color.RED));
                    findViewById(R.id.SetSceneCameraButton).setBackgroundColor(getColor(R.color.RED));
                } else {
                    ((SwitchMaterial) findViewById(R.id.AugmentSwitch)).setChecked(false);

                    updateVisualFromEvent(StreamEvents.CURRENT_SCENE,
                            streamStates.get(StreamEvents.CURRENT_SCENE));
                }
                break;
            case CHANGE_WITH_CLICKER:
                ((SwitchMaterial) findViewById(R.id.ChangeWithClickerSwitch)).setChecked(eventValue.equals("true"));
                break;
            case AUTO_CHANGE_TO_CAMERA:
                if (eventValue.equals("true"))
                    findViewById(R.id.TimerRunsButton).setBackgroundColor(getColor(R.color.GREEN));
                else  findViewById(R.id.TimerRunsButton).setBackgroundColor(getColor(R.color.RED));
            case STREAM_RUNNING:
            case STREAM_IS_SETUP:
            case STREAM_TITLE:
                //TODO maybe do something with this? I don't know yet
                break;
            case COMPUTER_SOUND_ON:
                if (eventValue.equals("true")){
                    findViewById(R.id.ComputerSoundButton).setBackground(
                            AppCompatResources.getDrawable(getApplicationContext(), R.drawable.volume_on));
                    ((TextView) findViewById(R.id.ComputerVolumeText)).setText(R.string.ComputerVolumeOn);
                } else {
                    findViewById(R.id.ComputerSoundButton).setBackground(
                            AppCompatResources.getDrawable(getApplicationContext(), R.drawable.volume_off));
                    ((TextView) findViewById(R.id.ComputerVolumeText)).setText(R.string.ComputerVolumeOff);
                }
                break;
            case STREAM_SOUND_ON:
                if(eventValue.equals("true")){
                    findViewById(R.id.StreamSoundButton).setBackground(
                            AppCompatResources.getDrawable(getApplicationContext(), R.drawable.volume_on));
                    ((TextView) findViewById(R.id.StreamVolumeText)).setText(R.string.StreamSoundOn);
                } else {
                    findViewById(R.id.StreamSoundButton).setBackground(
                            AppCompatResources.getDrawable(getApplicationContext(), R.drawable.volume_off));
                    ((TextView) findViewById(R.id.StreamVolumeText)).setText(R.string.StreamSoundOff);
                }
                break;
            case TIMER_TEXT:
                ((TextView) findViewById(R.id.TimerTextView)).setText(eventValue);
            case TIMER_NOT_RUNNING:
                break;
            case TIMER_LENGTH:
                EditText timerLengthInput =((EditText) findViewById(R.id.TimerLengthInput));
                timerLengthInput.setText(eventValue);

                int colorFrom = Color.GREEN;
                int colorTo = Color.BLACK;
                ValueAnimator colorAnimation = ValueAnimator.ofObject(new ArgbEvaluator(), colorFrom, colorTo);
                colorAnimation.setDuration(750); // milliseconds
                colorAnimation.addUpdateListener(
                        animator -> timerLengthInput.setTextColor((int) animator.getAnimatedValue()));
                colorAnimation.start();

                break;
        }
    }

    public void setExtraButtonHalo(Integer targetButton, Boolean isCamera){
        resetExtraButtonHalos(isCamera);

        Integer resource = activeExtrasMap.get(targetButton);
        if (resource != null){
            findViewById(targetButton).setForeground(AppCompatResources.getDrawable(
                    getApplicationContext(), resource));
        }
    }

    public void resetExtraButtonHalos(Boolean isCamera){
        if (isCamera){
            Integer resource = inactiveExtrasMap.get(currentCameraScene);

            if (resource != null){
                findViewById(currentCameraScene).setForeground(AppCompatResources.getDrawable(
                        getApplicationContext(), resource));
            }
        } else  {
            Integer resource = inactiveExtrasMap.get(currentScreenScene);
            if (resource != null){
                findViewById(currentScreenScene).setForeground(AppCompatResources.getDrawable(
                        getApplicationContext(), resource));
            }
        }
    }

    @OnLifecycleEvent(Lifecycle.Event.ON_RESUME)
    public void startPoll(){
        streamStates.setCallback(this::updateVisualFromEvent);
        socketService.setDoTheDialog(this::socketDialog);
        socketService.setUpdateNetworkStatusesRunnable(this::updateStatuses);
        socketService.updateAllStates();
        if (!socketService.socketShouldBeOpen()){
            socketDialog();
        }
    }
    @OnLifecycleEvent(Lifecycle.Event.ON_PAUSE)
    public void stopPoll(){
        streamStates.setCallback(null);
    }

    @OnLifecycleEvent(Lifecycle.Event.ON_DESTROY)
    public void killSocket(){
        streamStates.setCallback(null);
        socketService.setUpdateNetworkStatusesRunnable(null);
        socketService.closeSocket();
        unbindService(connection);
        socketIsBound = false;
    }

    public void updateStatuses(){
        WifiManager wifiManager = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
        String ssid = wifiManager.getConnectionInfo().getSSID();
        ((TextView) findViewById(R.id.WifiText)).setText(getString(R.string.WifiPlaceHolder, ssid));

        if (socketService != null){
            ((ImageView) findViewById(R.id.StatusImageView)).setImageTintList(ColorStateList.valueOf(
                    (socketService.socketShouldBeOpen()) ? getColor(R.color.GREEN) : getColor(R.color.RED)
            ));
        }
    }

    private boolean dialogIsOpen = false;
    public void socketDialog(){
        if (!dialogIsOpen) {
            DialogFragment dialog = new SocketAddressDialog(socketService.getIPAddress(),
                    socketService.getPort());
            dialog.show(getSupportFragmentManager(), "SocketAddressDialog");
            dialogIsOpen = true;
        }
    }

    public void onDialogPositiveClick(DialogFragment dialog, String IPAddress, String port) {
        System.out.println("HAPPY POSItive CliCKY NoiSEs");
        int intPort;
        intPort = Integer.parseInt(port);
        socketService.setNewAddress(IPAddress, intPort);
        dialogIsOpen = false;

    }
    public void onDialogNegativeClick(DialogFragment dialog) {
        System.out.println("sad negative clicky noises");
        socketService.closeSocket();
        dialogIsOpen = false;
    }

    public void socketErrorDialog(String message){
        DialogFragment dialog = new SocketErrorDialog(message);
        dialog.show(getSupportFragmentManager(), "SocketErrorDialog");
    }

    public void onSocketErrorDialogDismissal(){

    }


    public static void hideKeyboard(Activity activity) {
        InputMethodManager imm = (InputMethodManager) activity.getSystemService(Activity.INPUT_METHOD_SERVICE);
        //Find the currently focused view, so we can grab the correct window token from it.
        View view = activity.getCurrentFocus();
        //If no view currently has focus, create a new one, just so we can grab a window token from it
        if (view == null) {
            view = new View(activity);
        }
        imm.hideSoftInputFromWindow(view.getWindowToken(), 0);
    }

    public void onControllerButtonPress(View view){
        if (socketService.socketShouldBeOpen()){
            String socketMessage = buttonHandler.handleButtonPress(view);
            sendSocketData(socketMessage);
        } else {
            Snackbar.make(findViewById(R.id.MasterConstraint),
                    getString(R.string.SocketNotConnectedSnackBarText),
                    BaseTransientBottomBar.LENGTH_LONG).show();
        }
    }

    public void onTimerTimeInput(View view){
        onTimerTimeInput(findViewById(R.id.TimerLengthInput), EditorInfo.IME_ACTION_DONE, null);
    }

    public boolean onTimerTimeInput(TextView v, int actionId, KeyEvent event){
        hideKeyboard(this);
        v.clearFocus();
        if (actionId == EditorInfo.IME_ACTION_DONE) {
            String socketMessage = buttonHandler.handleTextView(v);

            sendSocketData(socketMessage);

            return true;
        }
        return false;
    }

    public void sendSocketData(String message){
        if (message != null && !message.isEmpty()){
            if (socketIsBound){
                socketService.sendData(message);
            }
        }
    }

    public void showHidePanel(View view){
        Integer target = panelControlsMap.get(view.getId());
        if (target != null){
            View targetPanel = findViewById(target);
            if (targetPanel.getVisibility() == View.VISIBLE) {
                targetPanel.setVisibility(View.GONE);
            } else {
                targetPanel.setVisibility(View.VISIBLE);
            }
        }
    }

    public void setKeepAwake(View view){
        SwitchMaterial switchMat = findViewById(R.id.StayOnSwitch);
        View masterView = findViewById(R.id.MasterConstraint);
        masterView.setKeepScreenOn(switchMat.isChecked());
    }


    public void wireButtons(){

        findViewById(R.id.TimerLengthSubmitButton).setOnClickListener(this::onTimerTimeInput);
        ((EditText) findViewById(R.id.TimerLengthInput)).setOnEditorActionListener(this::onTimerTimeInput);

        findViewById(R.id.StayOnSwitch).setOnClickListener(this::setKeepAwake);

        findViewById(R.id.WifiText).setOnClickListener((View view) -> {
            startActivity(new Intent(Settings.ACTION_WIFI_SETTINGS));
        });

        int[] idsForShowHidePanel = new int[]{
                R.id.ShowHideTopPanel,
                R.id.ShowHideTimerExtras,
                R.id.ShowHideSlideControls,
                R.id.ShowHideMediaControls,
                R.id.ShowHideRecordStreamPanel,
        };

        for (int i : idsForShowHidePanel){
            findViewById(i).setOnClickListener(this::showHidePanel);
        }

        int[] idsForOnControllerPress = new int[]{
                R.id.CameraBottomLeftButton,
                R.id.CameraBottomRightButton,
                R.id.ExtraBottomRightMiddle,
                R.id.ScreenBottomRightButton,
                R.id.CameraNoneButton,
                R.id.CameraTopRightButton,
                R.id.ScreenNoneButton,
                R.id.ScreenTopRightButton,
                R.id.ChangeWithClickerSwitch,
                R.id.AugmentSwitch,
                R.id.SetSceneCameraButton,
                R.id.SetSceneScreenButton,
                R.id.PrevSlideButton,
                R.id.NextSlideButton,
                R.id.TimerRunsButton,
                R.id.TimerLengthButton1,
                R.id.TimerLengthButton2,
                R.id.TimerLengthButton3,
                R.id.TimerLengthButton4,
                R.id.StreamSoundButton,
                R.id.ComputerSoundButton,
                R.id.MediaPausePlayButton,
            };

        for (int i : idsForOnControllerPress){
            findViewById(i).setOnClickListener(this::onControllerButtonPress);
        }
    }

}