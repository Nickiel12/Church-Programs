package com.example.livestreamcontroller;

import android.os.Build;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.RequiresApi;

import com.example.livestreamcontroller.SocketService.StreamStates;
import com.google.android.material.switchmaterial.SwitchMaterial;

@RequiresApi(api = Build.VERSION_CODES.N)
public class ButtonHandler {

    private StreamStates streamStates;

    ButtonHandler(StreamStates streamStates){
        this.streamStates = streamStates;
    }

    public void setStreamStates(StreamStates streamStates){this.streamStates = streamStates;}

    public String handleButtonPress(View view){
        if (view instanceof Button) {
            String buttonName = "", data = "";
            int id = view.getId();
            if      (id == R.id.CameraNoneButton)       buttonName = "Camera_None";
            else if (id == R.id.CameraTopRightButton)   buttonName = "Camera_Top_Right";
            else if (id == R.id.CameraBottomLeftButton) buttonName = "Camera_Bottom_Left";
            else if (id == R.id.CameraBottomRightButton)buttonName = "Camera_Bottom_Right";

            // What is this even doing???
            else if (id == R.id.ExtraBottomRightMiddle) buttonName = "ExtraBottomRightMid";

            else if (id == R.id.ScreenNoneButton)       buttonName = "Screen_None";
            else if (id == R.id.ScreenTopRightButton)   buttonName = "Screen_Top_Right";
            else if (id == R.id.ScreenBottomRightButton)buttonName = "Screen_Bottom_Right";

            else if (id == R.id.SetSceneCameraButton)   buttonName = "Scene_Camera";
            else if (id == R.id.SetSceneScreenButton)   buttonName = "Scene_Screen";
            else if (id == R.id.PrevSlideButton)        buttonName = "Prev_Slide";
            else if (id == R.id.NextSlideButton)        buttonName = "Next_Slide";

            else if (id == R.id.MediaPausePlayButton)   buttonName = "Media_Pause_Play";


            else if (id == R.id.TimerRunsButton) {
                buttonName = "Timer_Can_Run";
                data = streamStates.get(StreamEvents.TIMER_CAN_RUN);
                //These are inverted because we are taking the current state,
                //and telling the server to change it to the other one
                data = (data.equals("true")) ? "false" : "true";

            }
            else if (id == R.id.AugmentSwitch){
                buttonName = "Scene_Is_Augmented";
                data = (((SwitchMaterial) view).isChecked()) ? "true" : "false";
            }
            else if (id == R.id.ChangeWithClickerSwitch){
                buttonName = "Change_With_Clicker";
                data = (((SwitchMaterial) view).isChecked()) ? "true" : "false";
            }
            else if (id == R.id.ComputerSoundButton){
                buttonName = "Toggle_Computer_Volume";
                data = streamStates.get(StreamEvents.COMPUTER_SOUND_ON);
            }
            else if (id == R.id.StreamSoundButton){
                buttonName = "Toggle_Stream_Volume";
                data = streamStates.get(StreamEvents.STREAM_SOUND_ON);
            }

            if (id == R.id.TimerLengthButton1 || id == R.id.TimerLengthButton2
                || id == R.id.TimerLengthButton3 || id == R.id.TimerLengthButton4){

                double timerLength;

                if (id == R.id.TimerLengthButton1) timerLength = 5.0;
                else if (id == R.id.TimerLengthButton2) timerLength = 7.5;
                else if (id == R.id.TimerLengthButton3) timerLength = 15.0;
                else timerLength = 30.0; //this is if TimerLengthButton4

                return "{\"type\":\"Timer_Length\"," +
                        "\"data\":" + timerLength + "}";
            }

            StringBuilder output = new StringBuilder();
            output.append("{\"type\":\"button\",");
            output.append("\"button\":\"").append(buttonName).append("\"");

            if (data.isEmpty()) output.append("}");
            else output.append(",\"data\":\"").append(data).append("\"}");

            return output.toString();
        }
        return null;
    }

    public String handleTextView(TextView view){

        if (view.getId() == R.id.TimerLengthInput){
            double timerLength;

            timerLength = Double.parseDouble(view.getText().toString());

            return "{\"type\":\"Timer_Length\"," +
                    "\"data\":" + timerLength + "}";
        }
        else return "";
    }

}
