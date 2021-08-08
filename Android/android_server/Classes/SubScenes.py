

class SubScenes:
    class Camera:
        CAMERA_NONE = "Camera_None"
        CAMERA_TOP_RIGHT = "Camera_Top_Right"
        CAMERA_BOTTOM_RIGHT = "Camera_Bottom_Right"
        CAMERA_BOTTOM_LEFT = "Camera_Bottom_Left"

        @staticmethod
        def is_member(to_test):
            return ["Camera_None",
                    "Camera_Top_Right",
                    "Camera_Bottom_Right",
                    "Camera_Bottom_Left",
                    ].__contains__(to_test)

    class Screen:
        SCREEN_NONE = "Screen_None"
        SCREEN_TOP_RIGHT = "Screen_Top_Right"
        SCREEN_BOTTOM_RIGHT = "Screen_Bottom_Right"

        @staticmethod
        def is_member(to_test):
            return ["Screen_None",
                    "Screen_Top_Right",
                    "Screen_Bottom_Right",
                    ].__contains__(to_test)

    AUGMENTED = "Augmented"

    @staticmethod
    def is_member(to_test):
        return ["Camera_None",
                "Camera_Top_Right",
                "Camera_Bottom_Right",
                "Camera_Bottom_Left",
                "Screen_None",
                "Screen_Top_Right",
                "Screen_Bottom_Right",
                "Augmented",
                ].__contains__(to_test)
