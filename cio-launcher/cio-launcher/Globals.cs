using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace cio_launcher
{
    static class Globals
    {
        public static int current_state = Constants.STATE_STARTUP;
        public static string dl_base_link = "";

        public static Launcher launcher;
    }
}
