# veeam-python-test-task

## This is a task written in python to one-way synchronize folders

## How to setup

### Clone the repository
```bash
# Clone the repository
$ git clone git@github.com:Wantonfury/veeam-python-test-task.git
```

### Run the program
```bash
# Run the code using
$ python main.py -s source -r replica

# or with optional arguments
$ python main.py -s source -r replica -i 2 -l logs.txt
```

### The following arguments can be used:
- -s or --source to give the source folder path (must already exist)
- -r or --replica to give the target replica folder (does not need to exist beforehand)
- -i or --interval to set the synchronization interval (default 2 seconds)
- l or --logs to set the file where the logs are written (default logs.txt)