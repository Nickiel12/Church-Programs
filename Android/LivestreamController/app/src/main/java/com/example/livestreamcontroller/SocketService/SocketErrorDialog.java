package com.example.livestreamcontroller.SocketService;

import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.fragment.app.DialogFragment;

import com.example.livestreamcontroller.R;

public class SocketErrorDialog extends DialogFragment {

    public interface SocketErrorDialogListener {
        void onSocketErrorDialogDismissal();
    }

    SocketErrorDialogListener listener;

    String errorDialogMessage;

    public SocketErrorDialog(String dialogMessage){
        super();
        this.errorDialogMessage = dialogMessage;
    }

    @Override
    public void onAttach(@NonNull Context context){
        super.onAttach(context);
        listener = (SocketErrorDialogListener) context;
    }

    @NonNull
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState){
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        builder.setTitle(R.string.socket_error_dialog_title)
                .setMessage(errorDialogMessage)
                .setPositiveButton(R.string.socket_dialog_submit,
                        (dialogInterface, i) -> listener.onSocketErrorDialogDismissal());

        return builder.create();
    }
}
