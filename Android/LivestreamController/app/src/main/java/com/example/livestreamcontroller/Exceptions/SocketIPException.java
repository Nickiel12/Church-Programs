package com.example.livestreamcontroller.Exceptions;

public class SocketIPException extends Exception {
    public SocketIPException(){
        super("");
    }
    public SocketIPException(String message){
        super(message);
    }
}
