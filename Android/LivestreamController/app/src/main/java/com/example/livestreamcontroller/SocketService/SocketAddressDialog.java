package com.example.livestreamcontroller.SocketService;

import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.EditText;

import androidx.annotation.NonNull;
import androidx.fragment.app.DialogFragment;

import com.example.livestreamcontroller.R;

public class SocketAddressDialog extends DialogFragment {

    public interface SocketDialogListener {
        void onDialogPositiveClick(DialogFragment dialog, String IPAddress, String portNumber);
        void onDialogNegativeClick(DialogFragment dialog);
    }

    String IPAddress;
    int port;

    public SocketAddressDialog(String IPAddress, int port){
        super();
        this.IPAddress = IPAddress;
        this.port = port;
    }

    SocketDialogListener listener;

    @Override
    public void onAttach(@NonNull Context context){
        super.onAttach(context);
        listener = (SocketDialogListener) context;
    }

    @NonNull
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState){
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        LayoutInflater inflater = requireActivity().getLayoutInflater();

        View dialogView = inflater.inflate(R.layout.socket_dialog, null);
        ((EditText) dialogView.findViewById(R.id.socket_ip_address_edit_text)).setText(IPAddress);
        ((EditText) dialogView.findViewById(R.id.socket_port_edit_text))
                .setText(Integer.toString(port));
        builder.setView(dialogView)
                .setMessage(R.string.socket_dialog_message)

                .setPositiveButton(R.string.socket_dialog_submit,
                        (dialogInterface, i) -> listener.onDialogPositiveClick(this,
                                ((EditText) dialogView.findViewById(R.id.socket_ip_address_edit_text))
                                        .getText().toString(),
                                ((EditText) dialogView.findViewById(R.id.socket_port_edit_text))
                                        .getText().toString()))
                .setNegativeButton(R.string.socket_dialog_cancel,
                        (dialogInterface, i) -> listener.onDialogNegativeClick(this));

        return builder.create();
    }

}
