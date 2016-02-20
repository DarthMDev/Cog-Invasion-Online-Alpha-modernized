using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Threading;

namespace cio_login_server
{
    static class Constants
    {
        public const int CL_REQ_SERVER_INFO = 1;
        public const int SV_SERVER_INFO = 2;
        public const int CL_REQ_PLAY = 3;
        public const int CL_REQ_BASE_LINK = 4;
        public const int SV_BASE_LINK = 5;
        public const string LAUNCHER_VER = "1.0";
        public const string MSG_DELIMITER = ";";
        public const string DL_BASE_LINK = "http://download.coginvasion.com/";
    }

    class Client
    {
        public Client(List<Client> clients, TcpClient client, StreamReader sr, StreamWriter sw)
        {
            this.client = client;
            this.sr = sr;
            this.sw = sw;
            client_list = clients;
        }

        public void Process()
        {
            try
            {
                string request = sr.ReadLine();
                string[] split_msg = request.Split(Constants.MSG_DELIMITER.ToCharArray());

                if (split_msg[0] == Constants.CL_REQ_SERVER_INFO.ToString())
                {
                    Console.WriteLine("Client requested server info.");
                    Console.WriteLine("Server Version: " + Constants.LAUNCHER_VER);
                    string msg = Constants.SV_SERVER_INFO.ToString() + Constants.MSG_DELIMITER + Constants.LAUNCHER_VER;
                    sw.WriteLine(msg);
                    sw.Flush();
                }

                else if (split_msg[0] == Constants.CL_REQ_BASE_LINK.ToString())
                {
                    Console.WriteLine("Got base link request");
                    sw.WriteLine(Constants.SV_BASE_LINK + Constants.MSG_DELIMITER + Constants.DL_BASE_LINK);
                    sw.Flush();
                }

                else if (split_msg[0] == Constants.CL_REQ_PLAY.ToString())
                    Console.WriteLine("Got a play request.");

            }
            catch (Exception)
            {
                Console.WriteLine("Client dropped connection.");
                client_list.Remove(this);
            }
        }

        private TcpClient client;
        private StreamReader sr;
        private StreamWriter sw;
        private List<Client> client_list;
    }

    class Program
    {
        static async Task AcceptTcpClients(List<Client> clients, TcpListener listener, CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                var ws = await listener.AcceptTcpClientAsync();
                StreamReader sr = new StreamReader(ws.GetStream());
                StreamWriter sw = new StreamWriter(ws.GetStream());
                Console.WriteLine("Got a new connection.");
                clients.Add(new Client(clients, ws, sr, sw));
            }
        }

        static void Main(string[] args)
        {
            IPAddress ip = IPAddress.Parse("127.0.0.1");
            TcpListener listener = new TcpListener(ip, 7033);
            listener.Start();

            CancellationTokenSource cts = new CancellationTokenSource();

            // A list of clients
            List < Client > clients = new List<Client>();

            var task = AcceptTcpClients(clients, listener, cts.Token);

            while (true)
            {
                for (int i = 0; i <= clients.Count - 1; i++)
                {
                    Client client = clients[i];
                    client.Process();
                }
            }

        }

    }
}
