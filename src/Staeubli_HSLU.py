# Copyright 2017 - RoboDK Software S.L. - http://www.robodk.com/
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ----------------------------------------------------
# This file is a POST PROCESSOR for Robot Offline Programming to generate programs 
# for a Staubli (VAL3) robot with RoboDK
#
# To edit/test this POST PROCESSOR script file:
# Select "Program"->"Add/Edit Post Processor", then select your post or create a new one.
# You can edit this file using any text editor or Python editor. Using a Python editor allows to quickly evaluate a sample program at the end of this file.
# Python should be automatically installed with RoboDK
#
# You can also edit the POST PROCESSOR manually:
#    1- Open the *.py file with Python IDLE (right click -> Edit with IDLE)
#    2- Make the necessary changes
#    3- Run the file to open Python Shell: Run -> Run module (F5 by default)
#    4- The "test_post()" function is called automatically
# Alternatively, you can edit this file using a text editor and run it with Python
#
# To use a POST PROCESSOR file you must place the *.py file in "C:/RoboDK/Posts/"
# To select one POST PROCESSOR for your robot in RoboDK you must follow these steps:
#    1- Open the robot panel (double click a robot)
#    2- Select "Parameters"
#    3- Select "Unlock advanced options"
#    4- Select your post as the file name in the "Robot brand" box
#
# To delete an existing POST PROCESSOR script, simply delete this file (.py file)
#
# ----------------------------------------------------
# More information about RoboDK Post Processors and Offline Programming here:
#     http://www.robodk.com/help#PostProcessor
#     http://www.robodk.com/doc/en/PythonAPI/postprocessor.html
# ----------------------------------------------------


# ----------------------------------------------------
# Import RoboDK tools
from robodk import *
from robolink import *
import os
import platform
import shutil
import __main__


# Program.pjx file (references data file as %s.dtx)
PROGRAM_PJX = '''<?xml version="1.0" encoding="utf-8"?>
<Project xmlns="http://www.staubli.com/robotics/VAL3/Project/3">
<Parameters version="s7.5.3" stackSize="5000" millimeterUnit="true" />
<Programs>
<Program file="MoveJoint.pgx" />
<Program file="MoveLine.pgx" />
%s<Program file="start.pgx" />
<Program file="stop.pgx" />
<Program file="main.pgx" />
</Programs>
<Database>
<Data file="%s.dtx" />
</Database>
<Libraries />
</Project>
'''

MODULES_ADD = ''''''

PROGRAM_DTX = '''<?xml version="1.0" encoding="utf-8"?>
<Database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.staubli.com/robotics/VAL3/Data/2">
  <Datas>
    <!-- Frame decleration -->%s
    <!-- I/O decleration -->%s
    <!-- Tool decleration -->
    <Data name="tCurrentTool" access="private" xsi:type="array" type="tool" size="1">
      <Value key="0" %s fatherId="flange[0]" %s/>
    </Data>
    <!-- Point decleration -->
    <Data name="mCurrentSpeed" access="private" xsi:type="array" type="mdesc" size="1" />
    <Data name="pPointRx1" access="private" xsi:type="array" type="pointRx" size="1">
        <Value key="0" />
    </Data>
    <Data name="pPointRx2" access="private" xsi:type="array" type="pointRx" size="1">
        <Value key="0" />
    </Data>
  </Datas>
</Database>
'''

MOVELINE_PGX = '''<?xml version="1.0" encoding="utf-8"?>
<Programs xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.staubli.com/robotics/VAL3/Program/2">
  <Program name="MoveLine">
    <Parameters xmlns="http://www.staubli.com/robotics/VAL3/Param/1">
      <Parameter name="x_nX" type="num" xsi:type="element" />
      <Parameter name="x_nY" type="num" xsi:type="element" />
      <Parameter name="x_nZ" type="num" xsi:type="element" />
      <Parameter name="x_nRx" type="num" xsi:type="element" />
      <Parameter name="x_nRy" type="num" xsi:type="element" />
      <Parameter name="x_nRz" type="num" xsi:type="element" />
    </Parameters>
    <Code><![CDATA[begin
  pPointRx1.trsf.x = x_nX
  pPointRx1.trsf.y = x_nY
  pPointRx1.trsf.z = x_nZ
  pPointRx1.trsf.rx = x_nRx
  pPointRx1.trsf.ry = x_nRy
  pPointRx1.trsf.rz = x_nRz
  movel(pPointRx1,tCurrentTool,mCurrentSpeed)
end]]></Code>
  </Program>
</Programs>
'''

MOVEJOINT_PGX = '''<?xml version="1.0" encoding="utf-8"?>
<Programs xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.staubli.com/robotics/VAL3/Program/2">
  <Program name="MoveJoint">
    <Parameters xmlns="http://www.staubli.com/robotics/VAL3/Param/1">
      <Parameter name="x_nJ1" type="num" xsi:type="element" />
      <Parameter name="x_nJ2" type="num" xsi:type="element" />
      <Parameter name="x_nJ3" type="num" xsi:type="element" />
      <Parameter name="x_nJ4" type="num" xsi:type="element" />
      <Parameter name="x_nJ5" type="num" xsi:type="element" />
      <Parameter name="x_nJ6" type="num" xsi:type="element" />
    </Parameters>
    <Locals>
      <Local name="l_jJoint" type="joint" xsi:type="array" size="1" />
    </Locals>
    <Code><![CDATA[begin
  l_jJoint.j1 = x_nJ1
  l_jJoint.j2 = x_nJ2
  l_jJoint.j3 = x_nJ3
  l_jJoint.j4 = x_nJ4
  l_jJoint.j5 = x_nJ5
  l_jJoint.j6 = x_nJ6
  movej(l_jJoint,tCurrentTool ,mCurrentSpeed)
end]]></Code>
  </Program>
</Programs>
'''

MOVECIRC_PGX = '''<?xml version="1.0" encoding="utf-8"?>
<Programs xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.staubli.com/robotics/VAL3/Program/2">
  <Program name="MoveCirc">
    <Parameters xmlns="http://www.staubli.com/robotics/VAL3/Param/1">
      <Parameter name="x_nX" type="num" xsi:type="element" />
      <Parameter name="x_nY" type="num" xsi:type="element" />
      <Parameter name="x_nZ" type="num" xsi:type="element" />
      <Parameter name="x_nRx" type="num" xsi:type="element" />
      <Parameter name="x_nRy" type="num" xsi:type="element" />
      <Parameter name="x_nRz" type="num" xsi:type="element" />
      <Parameter name="x_nX2" type="num" xsi:type="element" />
      <Parameter name="x_nY2" type="num" xsi:type="element" />
      <Parameter name="x_nZ2" type="num" xsi:type="element" />
      <Parameter name="x_nRx2" type="num" xsi:type="element" />
      <Parameter name="x_nRy2" type="num" xsi:type="element" />
      <Parameter name="x_nRz2" type="num" xsi:type="element" />
    </Parameters>
    <Code><![CDATA[begin
  pPointRx1.trsf.x = x_nX
  pPointRx1.trsf.y = x_nY
  pPointRx1.trsf.z = x_nZ
  pPointRx1.trsf.rx = x_nRx
  pPointRx1.trsf.ry = x_nRy
  pPointRx1.trsf.rz = x_nRz
  pPointRx2.trsf.x = x_nX2
  pPointRx2.trsf.y = x_nY2
  pPointRx2.trsf.z = x_nZ2
  pPointRx2.trsf.rx = x_nRx2
  pPointRx2.trsf.ry = x_nRy2
  pPointRx2.trsf.rz = x_nRz2
  movec(pPointRx1,pPointRx2,tCurrentTool,mCurrentSpeed)
end]]></Code>
  </Program>
</Programs>
'''

MAIN_PGX = '''<?xml version="1.0" encoding="utf-8"?>
<Programs xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.staubli.com/robotics/VAL3/Program/2">
  <Program name="main">
    <Code><![CDATA[begin%s%s
    pPointRx1.config.shoulder = lefty
    pPointRx1.config.elbow = epositive
    pPointRx1.config.wrist = wpositive
    pPointRx2.config.shoulder = lefty
    pPointRx2.config.elbow = epositive
    pPointRx2.config.wrist = wpositive
    mCurrentSpeed.tvel = 100.00
    mCurrentSpeed.blend = joint
    mCurrentSpeed.reach = 0.010
    mCurrentSpeed.leave = 0.010
    %s
end]]></Code>
  </Program>
</Programs>'''

# start.pjx file (references data file as %s.dtx)
START_PGX = '''<?xml version="1.0" encoding="utf-8"?>
<Programs xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.staubli.com/robotics/VAL3/Program/2">
  <Program name="start">
    <Code><![CDATA[begin
  call main()
end]]></Code>
  </Program>
</Programs>
'''

STOP_PGX = '''<?xml version="1.0" encoding="utf-8"?>
<Programs xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.staubli.com/robotics/VAL3/Program/2">
  <Program name="stop">
    <Code><![CDATA[begin
end]]></Code>
  </Program>
</Programs>
'''

LOG_TXT = '''%s: GENERATED ROBOT PROGRAM WITH AROB STÄUBLI POSTPROCESSOR FOR STÄUBLI VAL 3:
%s
'''

INTERFACE = '''
<!DOCTYPE html SYSTEM "-//W3C//DTD VALHTML Strict//EN">
  <html xmlns="http://www.staubli.com/robotics/2016/03/valhtml">
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></meta>
      <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"></meta>
      <meta http-equiv="Pragma" content="no-cache"></meta>
      <meta http-equiv="Expires" content="0"></meta>
      <script type="text/javascript" src="/vendor/libs/stblUserPage.min.js"></script>
      <link href="/vendor/libs/up.min.v2.css" rel="stylesheet" media="all" type="text/css"></link>
      <meta name="src-version" content="8.10.2"></meta>
    </head>
    <body style="width: 480px; height: 690px; margin: 0">
      <label id="lbl1" style="width: 338px; height: 288px; text-align: center; top: 45px; position: absolute; left: 71px">Das gew&#228;hlte Programm beinhaltet<br/>Interaktionen &#252;ber dem Bediencontroller,<br/>welche hier angezeigt werden.</label>
    </body>
  </html>
'''

INTERFACE_BINDINGS = '''
{
  "version": "1.0",
  "bindings": [],
  "callbacks": [],
  "events": []
}
'''


def Pose_2_Staubli_v2(H):
    """Converts a pose to a Staubli target target"""
    x = H[0,3]
    y = H[1,3]
    z = H[2,3]
    a = H[0,0]
    b = H[0,1]
    c = H[0,2]
    d = H[1,2]
    e = H[2,2]
    if c > (1.0 - 1e-10):
        ry1 = pi/2
        rx1 = 0
        rz1 = atan2(H[1,0],H[1,1])
    elif c < (-1.0 + 1e-10):
        ry1 = -pi/2
        rx1 = 0
        rz1 = atan2(H[1,0],H[1,1])
    else:
        sy = c
        cy1 = +sqrt(1-sy*sy)
        sx1 = -d/cy1
        cx1 = e/cy1
        sz1 = -b/cy1
        cz1 = a/cy1
        rx1 = atan2(sx1,cx1)
        ry1 = atan2(sy,cy1)
        rz1 = atan2(sz1,cz1)
    return [x, y, z, rx1*180.0/pi, ry1*180.0/pi, rz1*180.0/pi]

# ----------------------------------------------------
def pose_2_str(pose):
    """Prints a pose target"""
    [x,y,z,r,p,w] = Pose_2_Staubli_v2(pose)
    return ('%.3f,%.3f,%.3f,%.3f,%.3f,%.3f' % (x,y,z,r,p,w))
    
def angles_2_str(angles):
    """Prints a joint target for Staubli VAL3 XML"""
    str = ''    
    for i in range(len(angles)):
        str = str + ('%.5f,' % (angles[i]))
    str = str[:-1]
    return str

def pose_2_str_dtx(pose):
    """Prints a pose target"""
    [x,y,z,r,p,w] = Pose_2_Staubli_v2(pose)
    return ('x="%.3f" y="%.3f" z="%.3f" rx="%.3f" ry="%.3f" rz="%.3f"' % (x,y,z,r,p,w)) 
    
def getSaveFolder(strdir='C:\\', strtitle='Save program folder ...'):
    import tkinter
    from tkinter import filedialog
    options = {}
    options['initialdir'] = strdir
    options['title'] = strtitle
    root = tkinter.Tk()
    root.withdraw()
    file_path = tkinter.filedialog.askdirectory(**options)
    return file_path

# I/O Class #
class Connection():
    def __init__(self, name, link, type):
        self.name = name
        self.link = link
        self.type = type

# ----------------------------------------------------    
# Object class that handles the robot instructions/syntax
class RobotPost(object):
    """Robot post object"""    
    # other variables
    ROBOT_POST = ''
    ROBOT_NAME = ''
    PROG_FILES = []
    PROG_NAME = 'unknown'
    MAIN_FOLDER = 'ProgRoboDK'
    PROG_PGX = ''
    PROG_MOVE_COUNT = 0
    LOG = ''
    LOG_LINES = 0
    LOG_ERROR = False
    REF = []
    REF_STRING = ''
    TOOL = eye(4)
    REF_COUNT = 0
    TOOL_COUNT = 0
    nAxes = 6
    TAB_PGX = '\t\t'
    PROG_PGX_LIST = []
    PROG_NAME_LIST = []
    SPEED = -1
    CON = []
    CON_STRING = ''
    GRIPPER = ''
    GRIPPER_SET = ''
    # Warning: if defaults are changed they must also be changed in main.pgx
    CONF_shoulder = 0   # 0=lefty       ; 1=righty
    CONF_lowerarm = 0   # 0=epositive   ; 1=enegative
    CONF_flip = 0       # 0=wpositive   ; 1=wnegative
    MOVEC_USED = 0
    INTERFACE_USED = False
    INTERFACE_CALL = '''\n\t\tuserPage("Interface")'''
    SETACCEL_USED = False
    # indent information
    IF_CONNECTION_COUNT = 0
    IF_CONFIRM_COUNT = 0
    # While variables
    WHILE_OBJECTS = {}
    WHILE_OPEN = ""
    WHILE_COUNT = 0
    
    
    def __init__(self, robotpost=None, robotname=None, robot_axes = 6, **kwargs):
        self.ROBOT_POST = robotpost
        self.ROBOT_NAME = robotname
        self.PROG = ''
        self.LOG = ''
        self.nAxes = robot_axes
        
    def ProgStart(self, progname):
        self.PROG_NAME = progname
        self.addline('// Program %s start' % progname)
        
    def ProgFinish(self, progname):
        self.addline('')
        self.addline('waitEndMove()')
        self.addline('// Program %s end' % progname)    
    
    def RemoveDirFTP(self, ftp, path):
        import ftplib
        """Recursively delete a directory tree on a remote server."""
        wd = ftp.pwd()
        try:
            names = ftp.nlst(path)
        except ftplib.all_errors as e:
            # some FTP servers complain when you try and list non-existent paths
            print('RemoveDirFTP: Could not remove {0}: {1}'.format(path, e))
            return

        for name in names:
            if os.path.split(name)[1] in ('.', '..'): continue
            print('RemoveDirFTP: Checking {0}'.format(name))
            try:
                ftp.cwd(name)  # if we can cwd to it, it's a folder
                ftp.cwd(wd)  # don't try a nuke a folder we're in
                self.RemoveDirFTP(ftp, name)
            except ftplib.all_errors:
                ftp.delete(name)

        try:
            ftp.rmd(path)
        except ftplib.all_errors as e:
            print('RemoveDirFTP: Could not remove {0}: {1}'.format(path, e))
    
    def UploadFTP(self, localpath):
        import ftplib
        
        robot = None
        try:
            RDK = Robolink()
            robot = RDK.Item(self.ROBOT_NAME, ITEM_TYPE_ROBOT)
            [server_ip, port, remote_path, username, password] = robot.ConnectionParams()
        except:
            server_ip = 'localhost'  # enter URL address of the robot it may look like: '192.168.1.123'
            username = 'username'     # enter FTP user name
            password = 'password'     # enter FTP password
            remote_path = '/usr/usrapp/session/default/saveTraj/CAD' # enter the remote path
        import sys
        while True:
            print("POPUP: Uploading program through FTP. Enter server parameters...")
            sys.stdout.flush()
            
            # check if connection parameters are OK
            values_ok = mbox('Using the following FTP connection parameters to transfer the program:\nRobot IP: %s\nRemote path: %s\nFTP username: %s\nFTP password: ****\n\nContinue?' % (server_ip, remote_path, username))
            if values_ok:
                print("Using default connection parameters")
            else:
                server_ip = mbox('Enter robot IP', entry=server_ip)
                if not server_ip:
                    print('FTP upload cancelled by user')
                    return
                remote_path = mbox('Enter the remote path (program folder) on the Staubli robot controller', entry=remote_path)
                if not remote_path:
                    return
                if remote_path.endswith('/'):
                    remote_path = remote_path[:-1]
                rob_user_pass = mbox('Enter user name and password as\nuser-password', entry=('%s-%s' % (username, password)))
                if not rob_user_pass:
                    return    
                name_value = rob_user_pass.split('-')
                if len(name_value) < 2:
                    password = ''
                else:
                    password = name_value[1]
                username = name_value[0]
            print("POPUP: <p>Connecting to <strong>%s</strong> using user name <strong>%s</strong> and password ****</p><p>Please wait...</p>" % (server_ip, username))
            #print("POPUP: Trying to connect. Please wait...")
            sys.stdout.flush()
            if robot is not None:
                robot.setConnectionParams(server_ip, port, remote_path, username, password)
            pause(2)
            try:
                myFTP = ftplib.FTP(server_ip, username, password)
                break;
            except:
                error_str = sys.exc_info()[1]
                print("POPUP: Connection to %s failed: <p>%s</p>" % (server_ip,error_str))
                sys.stdout.flush()
                contin = mbox("Connection to %s failed. Reason:\n%s\n\nRetry?" % (server_ip,error_str))
                if not contin:
                    return

        remote_path_prog = remote_path + '/' + self.MAIN_FOLDER
        myPath = r'%s' % localpath
        print("POPUP: Connected. Deleting existing files on %s..." % remote_path_prog)
        sys.stdout.flush()
        self.RemoveDirFTP(myFTP, remote_path_prog)
        print("POPUP: Connected. Uploading program to %s..." % server_ip)
        sys.stdout.flush()
        try:
            myFTP.cwd(remote_path)
            myFTP.mkd(self.MAIN_FOLDER)
            myFTP.cwd(remote_path_prog)
            #print('asdf')
        except:
            error_str = sys.exc_info()[1]
            print("POPUP: Remote path not found or can't be created: %s" % (remote_path))
            sys.stdout.flush()
            contin = mbox("Remote path\n%s\nnot found or can't create folder.\n\nChange path and permissions and retry." % remote_path)
            return
            
        def uploadThis(path):
            files = os.listdir(path)
            os.chdir(path)
            for f in files:
                if os.path.isfile(path + r'\{}'.format(f)):
                    print('  Sending file: %s' % f)
                    print("POPUP: Sending file: %s" % f)
                    sys.stdout.flush()
                    fh = open(f, 'rb')
                    myFTP.storbinary('STOR %s' % f, fh)
                    fh.close()
                elif os.path.isdir(path + r'\{}'.format(f)):
                    print('  Sending folder: %s' % f)
                    myFTP.mkd(f)
                    myFTP.cwd(f)
                    uploadThis(path + r'\{}'.format(f))
            myFTP.cwd('..')
            os.chdir('..')
        uploadThis(myPath) # now call the recursive function 

    def ProgSave(self, folder, progname, ask_user = False, show_result = False):
        if self.IF_CONNECTION_COUNT != 0:
            self.addlog("ERROR: You haven't closed %d of your ifConnection-conditions." % self.IF_CONNECTION_COUNT, True)
        if self.IF_CONFIRM_COUNT != 0:
            self.addlog("ERROR: You haven't closed %d of your ifConfirm-conditions." % self.IF_CONFIRM_COUNT, True)
        if self.WHILE_OPEN != "":
            self.addlog("ERROR: You haven't closed the while loop named %s." % self.WHILE_OPEN, True)
        
        self.close_module()
        added_modules = MODULES_ADD
        if self.MOVEC_USED:
            added_modules += '<Program file="MoveCirc.pgx" />\n'
            
        if ask_user or not DirExists(folder):
            foldersave = getSaveFolder(folder, 'Save program as...')
            if foldersave is not None and len(foldersave) > 0:
                foldersave = foldersave
            else:
                return
        else:
            foldersave = folder
        
        print("Saving program...")
        
        main_progname = 'Main' + progname

        folderprog = foldersave + '/' + progname
        self.MAIN_FOLDER = progname
        if not DirExists(folderprog):
            os.makedirs(folderprog)
        
        show_file_list = []
        folderprog_final = folderprog
            
        if not DirExists(folderprog_final):
            os.makedirs(folderprog_final)
        
        if not self.LOG_ERROR:
            #-----------------------------------
            # start.pgx
            start_file = folderprog_final + '/start.pgx'
            fid = open(start_file, "w")
            fid.write(START_PGX)
            fid.close()
            #-----------------------------------
            # stop.pgx
            stop_file = folderprog_final + '/stop.pgx'
            fid = open(stop_file, "w")
            fid.write(STOP_PGX)
            fid.close()
            #-----------------------------------
            # MoveJoint.pgx
            movej_file = folderprog_final + '/MoveJoint.pgx'
            fid = open(movej_file, "w")
            fid.write(MOVEJOINT_PGX)
            fid.close()
            #-----------------------------------
            # MoveLine.pgx
            movel_file = folderprog_final + '/MoveLine.pgx'
            fid = open(movel_file, "w")
            fid.write(MOVELINE_PGX)
            fid.close()
            # MoveCirc.pgx
            if self.MOVEC_USED:
                movec_file = folderprog_final + '/MoveCirc.pgx'
                fid = open(movec_file, "w")
                fid.write(MOVECIRC_PGX)
                fid.close()
            #-----------------------------------
            # program.PJX
            project_file = folderprog_final + '/%s.pjx' % self.PROG_NAME
            fid = open(project_file, "w")
            fid.write(PROGRAM_PJX % (added_modules, self.PROG_NAME))
            fid.close()
            print('SAVED: %s\n' % project_file)
            #-----------------------------------
            # program.dtx
            program_data = folderprog_final + '/%s.dtx' % self.PROG_NAME
            fid = open(program_data, "w")
            fid.write(PROGRAM_DTX % (self.REF_STRING, self.CON_STRING, pose_2_str_dtx(self.TOOL), self.GRIPPER))
            
            fid.close()
            #-----------------------------------
            # main.pgx
            main_data = folderprog_final + '/main.pgx'
            fid = open(main_data, "w")
            if not self.INTERFACE_USED:
                self.INTERFACE_CALL = ""
            fid.write(MAIN_PGX % (self.GRIPPER_SET, self.INTERFACE_CALL, self.PROG_PGX_LIST[0]))
            fid.close()
            # ----------------------------------
            # interface
            if self.INTERFACE_USED:
                interfacedir = folderprog_final + '/Interface'
                if not DirExists(interfacedir):
                    os.makedirs(interfacedir)
                interface_file = interfacedir + '/Interface.html'
                fid = open(interface_file, "w")
                fid.write(INTERFACE)
                fid.close()
                interface_bindings_file = interfacedir + '/Interface.bindings.json'
                fid = open(interface_bindings_file, "w")
                fid.write(INTERFACE_BINDINGS)
                fid.close()
        #-----------------------------------
        # log.txt
        from datetime import datetime
        if self.LOG_LINES==0:
            self.addlog("The program has been generated without any interruption.")
        
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log_file = folderprog_final + '/Debug_log.txt'
        fid = open(log_file, "w")
        fid.write(LOG_TXT % (dt_string, self.LOG))
        fid.close()
        #-----------------------------------  
        # copy tempfile in folder
        tempfile_src = __main__.__file__
        tempfile_dst = folderprog_final + '/Debug_tempfile.py'
        shutil.copy(tempfile_src, tempfile_dst)
        
        #self.UploadFTP(folderprog)
        self.PROG_FILES = folderprog
        
        if show_result:            
            if platform.system() == "Windows":
                if type(show_result) is str:
                    # Open file with provided application
                    import subprocess
                    subprocess.Popen([show_result, log_file])
                    if not self.LOG_ERROR:
                        subprocess.Popen([show_result, tempfile_dst])
                        subprocess.Popen([show_result, program_data])
                        subprocess.Popen([show_result, main_data])
                else:
                    # open file with default application
                    os.startfile(log_file)
                    if not self.LOG_ERROR:
                        os.startfile(program_data)
                        os.startfile(main_data)
                        os.startfile(tempfile_dst)
            else:
                # System is MacOS or Linux
                sCommand = "open"
                if platform.system() == "Linux":
                    sCommand = "xdg-open"
                elif platform.system() == "Darwin":
                    sCommand = "open"
                else: 
                    raise TypeError("Your OS "+platform.system()+" is not supported. Please contact me to implement your OS.")
                        
                os.system(sCommand+" "+log_file)
                if not self.LOG_ERROR:
                    os.system(sCommand+" "+tempfile_dst)
                    os.system(sCommand+" "+program_data)
                    os.system(sCommand+" "+main_data)
                
                
    # attempt FTP upload    
    def ProgSendRobot(self, robot_ip, remote_path, ftp_user, ftp_pass):
        """Send a program to the robot using the provided parameters. This method is executed right after ProgSave if we selected the option "Send Program to Robot".
        The connection parameters must be provided in the robot connection menu of RoboDK"""
        UploadFTP(self.PROG_FILES, robot_ip, remote_path, ftp_user, ftp_pass)
        
    def MoveJ(self, pose, joints, conf_RLF=None):
        """Add a joint movement"""
        self.setConfig(conf_RLF)
        self.addline('call MoveJoint(%s)' % angles_2_str(joints)) 
        
    def MoveL(self, pose, joints, conf_RLF=None):
        """Add a linear movement"""
        if pose is None:
            self.addlog("ERROR: Linear move must be a Cartesian target for VAL3", True)
        else:        
            self.addline('call MoveLine(%s)' % pose_2_str(pose))        

    def MoveC(self, pose1, joints1, pose2, joints2, conf_RLF_1=None, conf_RLF_2=None):
        """Add a circular movement"""
        self.MOVEC_USED = True
        self.addline('call MoveCirc(%s,%s)' % (pose_2_str(pose1),pose_2_str(pose2)))
        
    def setConfig(self, conf_RLF):
        if conf_RLF == None:
            rear = self.CONF_shoulder
            lowerarm = self.CONF_lowerarm
            flip = self.CONF_flip
        else:
            [rear, lowerarm, flip] = conf_RLF
            
        if rear != self.CONF_shoulder:
            self.addline('pPointRx1.config.shoulder = %s' % ("righty" if rear>0 else "lefty"))
            self.addline('pPointRx2.config.shoulder = %s' % ("righty" if rear>0 else "lefty"))
            self.CONF_shoulder = rear
        if lowerarm != self.CONF_lowerarm:
            self.addline('pPointRx1.config.elbow = %s' % ("enegative" if lowerarm>0 else "epositive"))
            self.addline('pPointRx2.config.elbow = %s' % ("enegative" if lowerarm>0 else "epositive"))
            self.CONF_lowerarm = lowerarm
        if flip != self.CONF_flip:
            self.addline('pPointRx1.config.wrist = %s' % ("wnegative" if flip>0 else "wpositive"))
            self.addline('pPointRx2.config.wrist = %s' % ("wnegative" if flip>0 else "wpositive"))
            self.CONF_flip = flip         
        
    def setFrame(self, pose, frame_id=None, frame_name=None):
        """Change the robot reference frame"""
        if frame_name == "world" or frame_name == "World":
            self.addlog("The frame can't be named 'world'. This is the basic frame of a staeubli application.", True)
            return False
        index = self.REF_COUNT
        try:
            index = self.REF.index(pose)
            self.addlog("INFO: Frame has already been entered")
        except:
            self.REF.append(pose)
            if frame_name == None or frame_name == "":
                frame_name = "noName%d" % self.REF_COUNT
            frame_name = str.replace(frame_name,'-','')
            frame_name = str.replace(frame_name,' ','')
            self.REF_STRING += '\n\t\t<Data name="%s" access="private" xsi:type="array" type="frame" size="1">' % frame_name
            self.REF_STRING += '\n\t\t\t<Value key="0" %s fatherId="world[0]" />' % pose_2_str_dtx(pose)
            self.REF_STRING += '\n\t\t</Data>'
            self.REF_COUNT += 1
        self.addline('link(pPointRx1,%s)' % frame_name, True)
        self.addline('link(pPointRx2,%s)' % frame_name, True)
        
    def setTool(self, pose, tool_id=None, tool_name=None):
        """Change the robot TCP"""
        if self.TOOL_COUNT > 1:
            self.addlog('WARNING: Only one tool allowed per program. Tool change skipped.')
            return
    
        self.TOOL = pose
        self.TOOL_COUNT = self.TOOL_COUNT + 1
        
    def Pause(self, time_ms):
        """Pause the robot program"""
        if time_ms < 0:
            self.addline('popUpMsg("Paused. Press OK to continue")')
        else:
            self.addline('waitEndMove()')
            self.addline('delay(%.3f)' % (time_ms*0.001))
            
    
    def setSpeed(self, speed_mms):
        """Changes the robot speed (in mm/s)"""
        self.setTranslationalSpeedTool(speed_mms)
    
    # following RoboDK-functions are replaced by the functions in "Library-speed-functions" #
    def setAcceleration(self, accel_mmss):
        if self.SETACCEL_USED:
            self.addlog("INFO: Stäubli Val3 has no implementation for linear acceleration.")
        else:
            self.SETACCEL_USED = True
    
    def setSpeedJoints(self, speed_degs):
        self.addlog("INFO: setSpeedJoints is not available in Stäubli VAL3. Use setSpeedPercentageJoints of the Stäubli-Library instead. See the documentation for further information.")
    
    def setAccelerationJoints(self, accel_degss):
        self.addlog("INFO: setAccelerationJoints is not available in Stäubli VAL3. Use setAccelerationPercentageJoints of the Stäubli-Library instead. See the documentation for further information.")
        
    def setZoneData(self, zone_mm):
        """Changes the zone data approach (makes the movement more smooth)"""
        self.addline('mCurrentSpeed.reach = %.3f' % zone_mm)
        self.addline('mCurrentSpeed.leave = %.3f' % zone_mm)
        
        
    # --------- Library-speed-functions ---------- #
    
    def setAccelerationPercentageJoints(self, percent):
        self.addline('mCurrentSpeed.accel = %.3f' % float(percent))
        
    def setDeccelerationPercentageJoints(self, percent):
        self.addline('mCurrentSpeed.decel = %.3f' % float(percent))
        
    def setSpeedPercentageJoints(self, percent):
        self.addline('mCurrentSpeed.vel = %.3f' % float(percent))
        
    def setTranslationalSpeedTool(self, speed):
        self.addline('mCurrentSpeed.tvel = %.3f' % float(speed))
        
    def setRotationalSpeedTool(self, speed):
        self.addline('mCurrentSpeed.rvel = %.3f' % float(speed))
       
    # --------- I/O functions ------------- #
    
    def addConnection(self, name, link, type):
        if not self.getConnection(name):
            self.CON.append(Connection(name,link,type))
            self.CON_STRING += '\n\t\t<Data name="%s" access="private" xsi:type="array" type="%s" size="1">' % (name, type)
            self.CON_STRING += '\n\t\t\t<Value key="0" link="%s" />' % link
            self.CON_STRING += '\n\t\t</Data>'

    def setGripperConnection(self, gripper):
        if self.checkConnection(gripper):
            connection = self.getConnection(gripper)
            self.GRIPPER = 'ioLink="%s"' % connection[0].link
            self.GRIPPER_SET = '\n\t\tclose(tCurrentTool)'

    def getConnection(self, name):
        ''' Returns a connection by name '''
        return list(filter(lambda x: x.name == name, self.CON))
    
    def checkConnection(self, connection):
        if not connection:
            self.addlog('WARNING: Connection %s has not been implemented. Do so before using it.' % name)
            return False
        else:
            return True
        
    def setOutput(self, name, value):
        connection = self.getConnection(name)
        if self.checkConnection(connection):
            self.addline('waitEndMove()')
            self.addline('%sSet(%s[0],%f)' % (connection[0].type, name, float(value)))
            
    def waitConnection(self, name, value, condition, timeout):
        connection = self.getConnection(name)
        if self.checkConnection(connection):
            self.addline('waitEndMove()')
            self.addline('watch(%sGet(%s[0]) %s %s, %d)' % (connection[0].type, name, condition, str(value), timeout))
            
    # ------------ IF Connections ----------- #        
            
    def ifConnection(self, name, value, condition):
        connection = self.getConnection(name)
        if self.checkConnection(connection):
            self.addline("waitEndMove()")
            self.addline('if %sGet(%s[0]) %s %s' % (connection[0].type, name, condition, str(value)))
            self.IF_CONNECTION_COUNT += 1
               
    def elseIfConnection(self, name, value, condition):
        connection = self.getConnection(name)
        if self.IF_CONNECTION_COUNT < 1:
            self.addlog("ERROR: ElseIf before opening if-condition.", True)
        else:
            if self.checkConnection(connection):
                self.IF_CONNECTION_COUNT -=1
                self.addline("waitEndMove()")
                self.addline('elseIf %sGet(%s[0]) %s %s' % (connection[0].type, name, condition, str(value)))
                self.IF_CONNECTION_COUNT +=1
            
    def elseConnection(self):
        if self.IF_CONNECTION_COUNT < 1:
            self.addlog("ERROR: Else before opening if-condition.", True)
        else:
            self.IF_CONNECTION_COUNT -=1
            self.addline("waitEndMove()")
            self.addline("else")
            self.IF_CONNECTION_COUNT +=1
            
    def endIfConnection(self):
        if self.IF_CONNECTION_COUNT < 1:
            self.addlog("ERROR: If-condition closed before opening one.", True)
        else:
            self.IF_CONNECTION_COUNT -= 1
            self.addline("endIf")
            
    # ------------ IF Confirm ------------ #
    
    def ifConfirm(self, message):
        self.INTERFACE_USED = True
        self.addline("waitEndMove()")
        self.addline('if userPageConfirm("%s")' % message)
        self.IF_CONFIRM_COUNT += 1

    def elseConfirm(self):
        if self.IF_CONFIRM_COUNT < 1:
            self.addlog("ERROR: Else before opening if-condition.", True)
        else:
            self.IF_CONFIRM_COUNT -=1
            self.addline("waitEndMove()")
            self.addline("else")
            self.IF_CONFIRM_COUNT +=1
    
    def endIfConfirmCount(self): 
        if self.IF_CONFIRM_COUNT < 1:
            self.addlog("ERROR: If-condition closed before opening one.", True)
        else:
            self.IF_CONFIRM_COUNT -= 1
            self.addline("endIf")
            
    # -------------- WHILE Connection --------------- #
    
    def whileIntern(self, whileName, conditionLine):
            if whileName not in self.WHILE_OBJECTS:
                self.WHILE_OBJECTS[whileName+"Parent"] = self.WHILE_OPEN
                self.WHILE_OBJECTS[whileName+"Code"] = ""
                self.WHILE_OPEN = whileName
                self.addline(conditionLine)
                self.WHILE_COUNT += 1
                self.WHILE_OBJECTS[whileName] = True
            else:
                self.WHILE_OBJECTS[whileName+"Finished"] = True
            self.WHILE_OPEN = whileName
            
    def endWhileIntern(self, whileName):
        if whileName in self.WHILE_OBJECTS:
            self.WHILE_OPEN = self.WHILE_OBJECTS[whileName+"Parent"]
            self.addcode(self.WHILE_OBJECTS[whileName+"Code"])
            self.WHILE_COUNT -= 1
            self.addline("endWhile")
            del self.WHILE_OBJECTS[whileName]
            if whileName+"Finished" in self.WHILE_OBJECTS:
                del self.WHILE_OBJECTS[whileName+"Finished"]
        else:
            self.addlog("ERROR: while-loop '%s' has not been implemented before." % whileName, True)
    
    def whileConnection(self, name, condition, value, whileName):
        connection = self.getConnection(name)
        if self.checkConnection(connection):
            self.whileIntern(whileName, 'while %sGet(%s[0]) %s %s' % (connection[0].type, name, condition, str(value)))
            
        
    def whileEndless(self, whileName):
        self.whileIntern(whileName, 'while true')
            
    def endWhileConnection(self, whileName):
        self.endWhileIntern(whileName)
    def endWhileEndless(self, whileName):
        self.endWhileIntern(whileName)
        
        
    def setDO(self, io_var, io_value):
        ''' LOG'''
      
    def waitDI(self, io_var, io_value, timeout_ms=-1):
        ''' LOG'''
        
    # ----- RunCode Functions ------ #
    
    def RunCode(self, code, is_function_call = False):
        """Adds code or a function call"""
        code="self."+code
        try:
            eval(code) #Please consider that eval is a bad practice, since the string code could contain a dangerous function call. Use this function on your own risk.
        except AttributeError:
            self.addlog("ERROR: Following function wasn't found: "+code, True)
            
    def waitSerialInput(self, link, value):
        self.addline('waitSI(...)')
            
        
    def RunMessage(self, message, iscomment = False):
        """Display a message in the robot controller screen (teach pendant)"""
        
        if iscomment:
            self.addline('// ' + message)
        else:
            self.addline('popUpMsg("%s")' % message)
            
            
    def boxAlert(self, message):
        self.INTERFACE_USED = True
        self.addline('waitEndMove()')
        self.addline('userPageAlert("%s")' % message)
        
# ------------------ private ----------------------                
    def addline(self, newline, noWhile = False):
        """Add a program line"""
        code = ""
        code += self.TAB_PGX
        tabCount = self.IF_CONNECTION_COUNT+self.IF_CONFIRM_COUNT+self.WHILE_COUNT
        if noWhile:
            tabCount -= 1
        for _ in range(tabCount):
            code += '\t'
        code += newline + '\n'
        self.addcode(code, noWhile)
            
    def addcode(self,code,noWhile=False):
        if self.WHILE_OPEN == "" or noWhile:
            self.PROG_PGX += code
        else:
            if (self.WHILE_OPEN+"Finished") not in self.WHILE_OBJECTS:
                self.WHILE_OBJECTS[self.WHILE_OPEN+"Code"] += code
        
    def addlog(self, newline, error=False):
        """Add a log message"""
        self.LOG_LINES += 1
        if self.LOG_LINES < 10:
            self.LOG += "0"
        self.LOG += str(self.LOG_LINES)
        self.LOG += ": "
        self.LOG += str(newline)
        self.LOG += '\n'
        
        if error:
            self.LOG_ERROR = True
            
    def close_module(self):
            
        progname = self.PROG_NAME
            
        self.PROG_PGX_LIST.append(self.PROG_PGX)
        self.PROG_NAME_LIST.append(progname)
        self.PROG_PGX = ''            
        # initialise next program
      