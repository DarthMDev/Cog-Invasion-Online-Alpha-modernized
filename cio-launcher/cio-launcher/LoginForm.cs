using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Windows.Forms;
using System.IO;

namespace cio_launcher
{
    public partial class LoginForm : Form
    {
        public LoginForm()
        {
            InitializeComponent();
        }

        private void play_btn_Click(object sender, EventArgs e)
        {

            if (Globals.current_state == Constants.STATE_LOGIN_MENU)
            {
                // Log in
                StreamWriter sw = Globals.launcher.sw;
                sw.WriteLine(Constants.CL_REQ_PLAY);
                sw.Flush();
            }
            else if (Globals.current_state == Constants.STATE_ACC_CREATE_MENU)
            {
                // Submit account
            }
            
        }

        private void create_acc_btn_Click(object sender, EventArgs e)
        {
            Globals.current_state = Constants.STATE_ACC_CREATE_MENU;
            this.back_btn.Show();
            this.play_btn.Text = "Done";
            this.login_lbl.Text = "Create An Account";
            this.login_lbl.Location = new Point(245, 160);
            this.create_acc_btn.Hide();
        }

        private void back_btn_Click(object sender, EventArgs e)
        {
            Globals.current_state = Constants.STATE_LOGIN_MENU;
            this.back_btn.Hide();
            this.play_btn.Text = "Play";
            this.login_lbl.Text = "Log-In";
            this.login_lbl.Location = new Point(270, 160);
            this.create_acc_btn.Show();
        }

        private void contact_btn_Click(object sender, EventArgs e)
        {
            Process.Start(Constants.CONTACT_LINK);
        }
    }
}
