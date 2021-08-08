package com.example.livestreamcontroller;

public interface StateChangeUiRunnable {
    void run(StreamEvents event, String value);
}
