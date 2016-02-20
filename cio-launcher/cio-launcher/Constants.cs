using System;

/// <summary>
/// Summary description for Constants
/// </summary>
public static class Constants
{
    public const string LOGIN_SERVER = "127.0.0.1";
    public const int LOGIN_PORT = 7033;

    public const int CL_SERVER_INFO = 1;
    public const int SV_SERVER_INFO = 2;
    public const int CL_REQ_PLAY = 3;
    public const int CL_REQ_BASE_LINK = 4;
    public const int SV_BASE_LINK = 5;

    public const string LAUNCHER_VER = "1.0";

    public const string MSG_DELIMITER = ";";

    public const int STATE_STARTUP = 0;
    public const int STATE_VALIDATING = 1;
    public const int STATE_LOGIN_MENU = 2;
    public const int STATE_ACC_CREATE_MENU = 3;
    public const int STATE_ACC_SUBMITTING = 4;
    public const int STATE_LOGGING_IN = 5;
    public const int STATE_GET_BASE_LINK = 6;
    public const int STATE_UPDATE_FILES = 7;
    public const int STATE_GEN_DL_LIST = 8;

    public const string CONTACT_LINK = "http://coginvasion.com/contact-us.html";
}
