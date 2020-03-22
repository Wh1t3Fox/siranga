# siranga
A ssh wrapper to make life a little bit easier. Why? I am lazy

### Installation

```bash
git clone https://github.com/Wh1t3Fox/siranga
cd siranga
pip3 install .
```


## Usage

#### Set Options

```
siranga →                                                                                                                                                                                       
Valid commands are: 
        !connect
        !hosts
        !active
        !set
        !kill
        !exit
siranga → !set                                                                                                                                                                                  

siranga → !set h                                                                                                                                                                                

    Add/Modify ssh_config entry
    Usage:
        Update Field:
            !set <host> <field_name> <value>
        Add Entry:
            !set <host> <hostname> <user> <port>
    
siranga → !set host1 172.17.0.4 root 22                                                                                                                                                         
siranga → !set                                                                                                                                                                                  
 Host   HostName    User  Port  IdentityFile  ProxyJump 
 host1  172.17.0.4  root  22    None          None      
 ```
 
 #### Connect to Host

```
siranga → !connect host1                                                                                                                                                                        
root@172.17.0.4's password: 
siranga (host1) → whoami                                             
root
```

#### Adding Host with ProxyJump
```
siranga → !set host2 172.17.0.5 root 22                                                                                                                                                         
siranga → !set                                                                                                                                                                                  
 Host   HostName    User  Port  IdentityFile   ProxyJump 
 host1  172.17.0.4  root  22    ~/.ssh/id_rsa  None      
 host2  172.17.0.5  root  22    None           None      
siranga → !set host2 ProxyJump host1                                                                                                                                                            
siranga → !set                                                                                                                                                                                  
 Host   HostName    User  Port  IdentityFile   ProxyJump 
 host1  172.17.0.4  root  22    ~/.ssh/id_rsa  None      
 host2  172.17.0.5  root  22    None           host1     
siranga → !connect host2                                                                                                                                                                        
root@172.17.0.4's password: 
root@172.17.0.5's password: 
siranga [→host1→] (host2) → ls -lAhrt                                                                                                                                                           
bash: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)
total 16K
-rw-r--r-- 1 root root  148 Aug 17  2015 .profile
-rw-r--r-- 1 root root 3.1K Apr  9  2018 .bashrc
-rw------- 1 root root  917 Mar 22 01:57 .viminfo
drwx------ 2 root root 4.0K Mar 22 01:59 .cache

siranga [→host1→host1→] (host2) → uname -a                                                                                                                                                      
Linux 9d904948ecf0 5.5.10-arch1-1 #1 SMP PREEMPT Wed, 18 Mar 2020 08:40:35 +0000 x86_64 x86_64 x86_64 GNU/Linux 
```

#### Run remote commands

```
siranga (host1) → w                                                                                                                                                                             
bash: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)
 01:54:24 up  3:54,  0 users,  load average: 0.22, 0.34, 0.33
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT

siranga (host1) → ls -lAhrt                                               
total 16K
-rw-r--r-- 1 root root  148 Aug 17  2015 .profile
-rw-r--r-- 1 root root 3.1K Apr  9  2018 .bashrc
-rw------- 1 root root  941 Mar 22 01:51 .viminfo
drwx------ 2 root root 4.0K Mar 22 01:51 .cache

```

Disconnect from host but keep socket alive

```
siranga (host1) → !disconnect                                                                                                                                                                   
siranga → !active                                                                                                                                                                               
host1
```

### Features
- Multiplexing
- Upload
- Download
- Socks Proxy
- Reverse Tunnel
- Forward Tunnel
