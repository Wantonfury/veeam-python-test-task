
import os, sys, logging, argparse, threading, hashlib

# Check if file is synchronized
def checkFileExists(file):
  if os.path.isfile(file):
    return True
  return False

# Check if two files have the same md5 checksum
def checkFileChecksum(fileSource, fileReplica):
  checksum = False
  
  with open(fileSource) as source:
    with open(fileReplica) as replica:
      if hashlib.md5(source.read().encode("utf-8")).hexdigest() == hashlib.md5(replica.read().encode("utf-8")).hexdigest():
        checksum = True
  
  return checksum

# Read source file and update replica file to match if checksum is different
def syncFiles(fileSource, fileReplica):
  fileExists = checkFileExists(fileReplica)
  
  # If file does not exist there is no point in checking checksum
  if fileExists and checkFileChecksum(fileSource, fileReplica):
    return
  
  with open(fileSource, "r") as source:
    with open(fileReplica, "w") as replica:
      if fileExists:
        logging.info("Updating file: " + fileReplica)
      else:
        logging.info("Creating file: " + fileReplica)
      
      replica.write(source.read())

# This is called every interval to check and synchronize
def update(args):
  replicaFiles = []
  foldersSource = []
  
  # Synchronize source files
  for (dirpath, dirnames, filenames) in os.walk(args.source):
    replicaPath = dirpath.replace(args.source, args.replica) # The path to the replica folder
    foldersSource.append(replicaPath) # Keep track of folders that should be in replica
    
    # Create folders
    for dir in dirnames:
      folder = os.path.join(replicaPath, dir)
      if not os.path.isdir(folder):
        logging.info("Creating folder: " + folder)
        os.mkdir(folder)
    
    for filename in filenames:
      fileSource = os.path.join(dirpath, filename)
      fileReplica = os.path.join(replicaPath, filename)
      
      replicaFiles.append(fileReplica) # Keep track of files that should be in replica folder
      
      syncFiles(fileSource, fileReplica)
  
  # Remove non-source files in replica
  for (dirpath, dirnames, filenames) in os.walk(args.replica, topdown=False):
    for filename in filenames:
      file = os.path.join(dirpath, filename)
      
      # If file should not be in replica folder then delete it
      if not file in replicaFiles:
        logging.info("Deleting file: " + file)
        os.remove(file)
    
    # Synchronize removed folders
    for dir in dirnames:
      folder = os.path.join(dirpath, dir)
      if folder not in foldersSource:
        logging.info("Remove folder: " + folder)
        os.rmdir(folder)
  

# A function used to repeatedly call update at a regular interval
def updateThread(args):
  threading.Timer(interval=args.interval, function=updateThread, kwargs={'args': args}).start()
  update(args)

if __name__ == "__main__":
  # Parse arguments
  parser = argparse.ArgumentParser(description="Synchronize two folders at a specific interval and log any changes.")
  parser.add_argument("-s", "--source", required=True, help="name of local source folder", type=str, dest="source")
  parser.add_argument("-r", "--replica", required=True, help="name of local replica folder", type=str, dest="replica")
  parser.add_argument("-l", "--logs", required=False, help="name of logs file (default: logs.txt)", type=str, dest="logs", default="logs.txt")
  parser.add_argument("-i", "--interval", required=False, help="interval in seconds used when synchronizing (default: 2.0)", default=2.0, type=float, dest="interval")
  args = parser.parse_args()
  
  # Check if source folder exists, if not then exit
  if not os.path.isdir(args.source):
    print("Source \"" + os.getcwd() + "\\" + args.source + "\" folder not found.")
    sys.exit(1)
  
  # Create replica folder if it does not already exist
  if not os.path.isdir(args.replica):
    os.mkdir(args.replica)
  
  # Configure the logging
  logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", handlers=[
    logging.FileHandler(args.logs, mode="w"),
    logging.StreamHandler(sys.stdout)
  ])
  
  # Log arguments
  logging.info("Synchronization initialized with: source=" + args.source + ", replica=" + args.replica + " logs=" + args.logs + " interval=" + str(args.interval))
  
  # Start the synchronization interval
  updateThread(args)