using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Threading;
using System.Net;
using System.Net.Sockets;
using System.Windows.Forms;
using System.Security.Cryptography;

namespace cio_launcher
{
    public class Launcher
    {
        /// <summary>
        /// An async task that checks for incoming messages from the server and responds to them.
        /// </summary>
        static async Task Listen(Launcher launcher, CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                string msg = await launcher.sr.ReadLineAsync();
                if (msg != null)
                {
                    // Split the message up into chunks for processing using the delimiter
                    string[] split_msg = msg.Split(Constants.MSG_DELIMITER.ToCharArray());

                    if (split_msg[0] == Constants.SV_SERVER_INFO.ToString() && Globals.current_state == Constants.STATE_VALIDATING)
                    {
                        string server_ver = split_msg[1];
                        if (Constants.LAUNCHER_VER == server_ver)
                        {
                            // We have connected, our launcher is validated, let's fetch the download info
                            Globals.current_state = Constants.STATE_GET_BASE_LINK;
                            Console.WriteLine("Launcher validated.");
                            // Send the dl base link request
                            launcher.sw.WriteLine(Constants.CL_REQ_BASE_LINK.ToString());
                            launcher.sw.Flush();
                        }
                    }

                    else if (split_msg[0] == Constants.SV_BASE_LINK.ToString() && Globals.current_state == Constants.STATE_GET_BASE_LINK)
                    {
                        string base_link = split_msg[1];
                        Console.WriteLine("Base link: " + base_link);
                        Globals.dl_base_link = base_link;

                        // Now that we have the base link begin to generate a download list.
                        Globals.current_state = Constants.STATE_GEN_DL_LIST;
                        launcher.BeginGenerateDLList();
                    }

                }
            }
        }

        public void BeginGenerateDLList()
        {
            // Download the hash file (synchronous)
            Console.WriteLine("Downloading hash file");
            WebRequest req = WebRequest.Create(Globals.dl_base_link + "file_info.txt");
            WebResponse resp = req.GetResponse();
            Stream stream = resp.GetResponseStream();
            StreamReader dlSr = new StreamReader(stream);
            ProcessHashFile(dlSr);
        }

        private void ProcessHashFile(StreamReader dlSr)
        {
            Console.WriteLine("Processing hash file");
            while (dlSr.Peek() >= 0)
            {
                string fileData = dlSr.ReadLine();
                if (fileData.Length == 0 || fileData.Substring(0, 2) == "//")
                    continue;

                string[] split_data = fileData.Split(' ');
                string filename = split_data[0];
                string md5 = split_data[1];
                if (!IsSameMD5(filename, md5))
                {
                    Console.WriteLine(filename + " is out of date or missing! Adding to download list.");
                    dl_list.Add(filename);
                }
                else
                    Console.WriteLine(filename + " is up to date!");
            }
            if (dl_list.Count > 0)
            {
                Console.WriteLine("Will download files: ");
                string output = "";
                foreach (string file in dl_list)
                {
                    if (dl_list.IndexOf(file) < dl_list.Count - 1)
                        output += file + ", ";
                    else
                        output += file;
                }
                Console.WriteLine(output);
            }
            else
                Console.WriteLine("All files are up to date!");

            // We're good to go! Start the windows forms!
            LaunchWindowsForms();
        }

        private bool IsSameMD5(string filename, string md5)
        {
            if (!File.Exists(filename))
                return false;
            else
            {
                string myMD5 = BitConverter.ToString(new SHA1CryptoServiceProvider().ComputeHash(File.Open(filename, FileMode.Open)));
                return (myMD5 == md5);
            }
        }

        private void LaunchWindowsForms()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            LoginForm lf = new LoginForm();
            this.lf = lf;
            Application.Run(lf);
        }

        public Launcher()
        {
            string gameserver = Constants.LOGIN_SERVER + ":" + Constants.LOGIN_PORT.ToString();
            Console.WriteLine("Connecting to login server at " + gameserver);

            // Connect to the server
            TcpClient client = new TcpClient();
            this.client = client;
            try
            {
                client.Connect(Constants.LOGIN_SERVER, Constants.LOGIN_PORT);
            }
            catch (SocketException)
            {
                Console.WriteLine("Could not connect to the login server.");
                return;
            }

            Console.WriteLine("Connected");

            // Initialize our stream readers and writers for talking to the server
            StreamReader sr = new StreamReader(client.GetStream());
            this.sr = sr;
            StreamWriter sw = new StreamWriter(client.GetStream());
            this.sw = sw;

            List<string> dl_list = new List<string>();
            this.dl_list = dl_list;

            // Start the reader task
            CancellationTokenSource cts = new CancellationTokenSource();
            this.cts = cts;
            var listen_task = Listen(this, cts.Token);

            Console.WriteLine("Now sending server info req");

            // We are now validating our launcher
            Globals.current_state = Constants.STATE_VALIDATING;
            // Send the server info req
            sw.WriteLine(Constants.CL_SERVER_INFO);
            sw.Flush();

            Application.Run();

        }

        private TcpClient client;
        public StreamReader sr;
        public StreamWriter sw;
        private CancellationTokenSource cts;
        private LoginForm lf;
        private List<string> dl_list;

    }
}
