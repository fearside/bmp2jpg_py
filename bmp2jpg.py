#!/usr/bin/python
import sys, os, re, time, resource
# Turn off traceback
#sys.tracebacklimit = 0

# bcolors - simple color coding
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Try to import image lib
try:
    import Image
except ImportError:
    print bcolors.FAIL + "! Can't import Image lib." + bcolors.ENDC
    print bcolors.FAIL + "! For Debian/Ubuntu sudo apt-get install python-imaging" + bcolors.ENDC
    print bcolors.FAIL + "! For CentOS/RedHat sudo yum install python-imaging" + bcolors.ENDC
    os._exit(99)

if len(sys.argv) < 2:
    print bcolors.FAIL + "! Less than 2 arguments given, exiting." + bcolors.ENDC
    print bcolors.WARNING + "! Usage, " + bcolors.OKBLUE + os.path.basename(sys.argv[0]) + bcolors.OKGREEN + " if=inputdir of=outputdir" + "progressbar=[" + bcolors.WARNING + "false" + bcolors.OKGREEN + "|true]" + bcolors.ENDC
    os._exit(98)

# Set start time
tic = time.clock()

# Author and script information
__status__ = "Production" # Statuses allowed is Prototype, Development & Production
__author__ = "Teddy Skarin"
__function__ = "Converts a BMP file to a JPEG file."
__copyright__ = "XYZ"
__credits__ = ["T1", "T2", "T3", "T4"]
__license__ = "GPL"
__version__ = "0.7d" # Version statuses are X.X followed by an p(prototype),d(development) or P(Production) marker
__maintainer__ = "Teddy Skarin"
__email__ = "teddy.skarin@gmail.com"
__script__ = os.path.basename(sys.argv[0])

# Define variables
outputDirectory = ""
inputDirectory = ""
progressBar = ""
returnCode = 0
errorFiles = 0
fileCount = 0
numberOfFiles = 0
bytesWritten = 0
bytesRead = 0
filesWritten = 0
fileList = ""
fileExtInput = "[bB][mM][pP]"
fileExtOutput = "jpg"
writeToLog = True
logDest = '/tmp/' + __script__ + '_' + str(time.strftime("D%Y-%m-%d_T%H-%M")) + '.log'

# Loop through input arguments
for arg in sys.argv[1:]:
    if re.match('if\=.*', arg):
        if not inputDirectory:
            inputDirectory = arg[3:]

    if re.match('of\=.*', arg):
        if not outputDirectory:
            outputDirectory = arg[3:]

    if re.match('progressbar\=.*', arg):
        if not progressBar and arg[12:] == "true":
            progressBar = arg[12:]

if not progressBar:
    progressBar = "false"


# Start of definitions

# Print header info
def printInfo():
    print bcolors.HEADER + '=> Script   : ' + __script__ + bcolors.ENDC
    print bcolors.HEADER + '=> Function : ' + __function__ + bcolors.ENDC
    print bcolors.HEADER + '=> Author   : ' + __author__ + bcolors.ENDC
    print bcolors.HEADER + '=> Status   : ' + __status__ + bcolors.ENDC
    print bcolors.HEADER + '=> Version  : ' + __version__ + bcolors.ENDC

# Print finishing info
def printFinish():
    print bcolors.OKGREEN + '+ Processing finished' + bcolors.ENDC
    filesPerSecond = fileCount / round(toc,2)
    print(bcolors.OKGREEN + '+ Time used, ' + str(round(toc,2)) + ' seconds(' + str(round(filesPerSecond,2)) + ' files/sec)' + bcolors.ENDC)
   # Calculate memory usage
    memUsage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    memCalc = memUsage / 1024 / 1024
    print bcolors.OKGREEN + '+ Memory used, ' + str(round(memCalc,2))+ 'Mb' + bcolors.ENDC
    global filesWritten
    print bcolors.OKGREEN + '+ Files written, ' + str(filesWritten) + bcolors.ENDC
    if errorFiles != 0:
        print bcolors.FAIL + '+ Bad file(s), ' + str(errorFiles) + bcolors.ENDC
    global bytesRead
    bytesRead = round(bytesRead / 1024 / 1024, 2)
    print bcolors.OKGREEN + '+ Bytes read, ' + str(bytesRead) + 'Mb' + bcolors.ENDC
    global bytesWritten
    bytesWritten = round(bytesWritten / 1024 / 1024, 2)
    print bcolors.OKGREEN + '+ Bytes written, ' + str(bytesWritten) + 'Mb' + bcolors.ENDC

    # Write to log section
    if writeToLog == True:
        logFile.write(time.strftime("%Y-%m-%d %H:%M:%S") + ' + Processing finished\n')
        logFile.write(time.strftime("%Y-%m-%d %H:%M:%S") + ' + Time used, ' + str(round(toc,2)) + ' seconds(' + str(round(filesPerSecond,2)) + ' files/sec)\n')
        logFile.write(time.strftime("%Y-%m-%d %H:%M:%S") + ' + Memory used, ' + str(round(memCalc,2))+ 'Mb\n')
        logFile.write(time.strftime("%Y-%m-%d %H:%M:%S") + ' + File(s) written, ' + str(filesWritten) + '\n')
        if errorFiles != 0:
            logFile.write(time.strftime("%Y-%m-%d %H:%M:%S") + ' ! Bad file(s), ' + str(errorFiles) + '\n')
        logFile.write(time.strftime("%Y-%m-%d %H:%M:%S") + ' + Bytes read, ' + str(bytesRead) + 'Mb\n')
        logFile.write(time.strftime("%Y-%m-%d %H:%M:%S") + ' + Bytes written, ' + str(bytesWritten) + 'Mb\n')
        logFile.close()


# Progressbar updater
def update_progress(progressBar):
    barLength = 40 # Modify this to change the length of the progress bar
    status = ""
    block = int(round(barLength*progressBar))
    #fill = '\xe2\x96\x88' # Only for *nix terminals
    #blank = '\xe2\x96\x91' # Only for *nix terminals
    fill = '#'
    blank = '-'
    #marker=unichr(9618).encode("utf-8"),
    #text = bcolors.OKGREEN + "\r[ + ] Progress: [{0}] {1}% {2}".format('#'*block + '-'*(barLength-block), round(progressBar*100,1), status) + bcolors.FAIL + '[' + str(errorFiles) + ']' + bcolors.ENDC
    #text = bcolors.OKGREEN + "\r+ Progress: [{0}] {1}% {2}".format(fill*block + blank*(barLength-block), round(progressBar*100,1), status) + bcolors.FAIL + '[' + str(errorFiles) + ']' + bcolors.ENDC
    text = bcolors.OKGREEN + "\r+ Progress: [" + bcolors.ENDC + "{0}".format(fill*block + blank*(barLength-block)) + bcolors.OKGREEN + "] {0}% {1}".format(round(progressBar*100,1), status) + bcolors.FAIL + '[' + str(errorFiles) + ']' + bcolors.ENDC
    sys.stdout.write(text)
    sys.stdout.flush()

# Define return code handling
def incrementReturnCode():
    global returnCode
    returnCode += 1

# Define increment of files written
def incrementFilesWritten():
    global filesWritten
    filesWritten += 1

# Define increment error files
def incrementErrorFiles():
    global errorFiles
    errorFiles += 1

def checkReturnCode():
    global returnCode
    global logFile
    if returnCode > 0:
        logFile.write(time.strftime("%Y-%m-%d %H:%M:%S") + '[E:' + str(returnCode) + '] Something broke, please take care\n')
        os._exit(returnCode)

def createLogFile():
    global logFile
    global writeToLog
    # Open logfile
    try:
        logFile = open(logDest, 'w')
    except:
        print bcolors.FAIL + "! Can't open logfile, continuing processing without logging." + bcolors.ENDC
        writeToLog = False

    if writeToLog == True:
        print bcolors.WARNING + "+ Logfile set to, " + bcolors.OKGREEN + str(logDest) + bcolors.ENDC
        # Write header to log
        logFile.write(str(time.strftime("%Y-%m-%d %H:%M:%S")) + ' + Processing started\n')

def checkInputDirectory(inputDirectory):
    if not os.path.exists(inputDirectory):
        print bcolors.WARNING + "! Input directory, " + bcolors.FAIL + inputDirectory + bcolors.WARNING + " , dosent exist, please take care" + bcolors.ENDC
        incrementReturnCode()
    else:
        if os.access(inputDirectory, os.R_OK):
            print bcolors.WARNING + "+ Input directory set to, " + bcolors.OKGREEN + inputDirectory + bcolors.ENDC

def checkOutputDirectory(outputDirectory):
    # Check if directory exists, if not, create
    if not os.path.exists(outputDirectory):
         try:
            os.makedirs(outputDirectory)
            print bcolors.WARNING + "+ Output directory created and set to, " + bcolors.OKGREEN + outputDirectory + bcolors.ENDC
         except:
            print bcolors.WARNING + "! Couldn't create output directory, " + bcolors.FAIL + outputDirectory + bcolors.ENDC
            incrementReturnCode()
    # Check if the directory isn't writable
    elif not os.access(outputDirectory, os.W_OK) and os.access(outputDirectory, os.R_OK) and os.access(outputDirectory, os.X_OK):
            print bcolors.WARNING + "! Output directory set to, " + bcolors.FAIL + outputDirectory + \
                  bcolors.WARNING +  "\n * INFO : Output directory already exists and is "+ bcolors.FAIL + "NOT" + bcolors.WARNING +" writeable. Exiting." + bcolors.ENDC
            incrementReturnCode()
    # Check if directory is workable
    elif os.access(outputDirectory, os.W_OK) and os.access(outputDirectory, os.R_OK) and os.access(outputDirectory, os.X_OK):
            print bcolors.WARNING + "+ Output directory set to, " + bcolors.OKGREEN + outputDirectory + \
                  bcolors.WARNING + "\n * INFO : Output directory already exists and is writeable." + bcolors.ENDC

def buildFileList():
    global fileList
    fileList = [ f for f in os.listdir(inputDirectory) if re.match('.*\.' + fileExtInput + '$', f) ]
    if not len(fileList) > 0:
        print bcolors.WARNING + " ! Can't find any files matching, " + bcolors.FAIL + fileExtInput + bcolors.ENDC
        incrementReturnCode()
    else:
        print bcolors.WARNING + "+ Found " + bcolors.OKGREEN + str(len(fileList)) + bcolors.WARNING + " file(s)." + bcolors.ENDC
        return fileList

# Start of main script

# Print header info
printInfo()

# Open logfile
createLogFile()

# Perform input directory check
checkInputDirectory(inputDirectory)

# Check for return code
checkReturnCode()

# Perform output directory actions
checkOutputDirectory(outputDirectory)

# Check for return code
checkReturnCode()

# Build file list for file conversion
buildFileList()

# Fetch number of files in filelist
numberOfFiles = len(fileList)


# Write processing start
if progressBar != "true":
    print bcolors.WARNING + "+ Processing started" + bcolors.ENDC

# Loop through file list
for file in fileList:
    fileCount += 1
    # Set input filename and open input file, readbyte
    inputImage = os.path.realpath(os.path.join(inputDirectory,file))
    # Fetch extension of file
    extension = os.path.splitext(inputImage)[1]
    # Build output file
    outputImage = os.path.realpath(os.path.join(outputDirectory,file))
    outputImage = outputImage.replace(extension, '.' + fileExtOutput)

    try:
        im = Image.open(inputImage).convert('RGB').save(outputImage)
        if os.path.exists(outputImage) and os.path.getsize(outputImage) > 0:
            incrementFilesWritten()
            bytesWritten += os.path.getsize(outputImage)
            bytesRead += os.path.getsize(inputImage)
        # Update progress bar
        if progressBar and progressBar == "true":
            update_progress(fileCount/float(numberOfFiles))
    except IOError as e:
        ConvertCommand = 'convert ' + inputImage + ' -quality 80 ' + outputImage
        # Fixa till detta åt victor - kolla först om convert finns, sen kör, annars rapportera fel. SystemError OSError
        os.system(ConvertCommand)
        bytesRead += os.path.getsize(inputImage)
        incrementErrorFiles()
        if writeToLog == True:
            logFile.write(str(time.strftime("%Y-%m-%d %H:%M:%S")) + " [E] " + str(e) + ", " + file + '\n')
        if progressBar and progressBar == "true":
            update_progress(fileCount/float(numberOfFiles))

# Check if we are using a progressbar and add a return at the end
if progressBar and progressBar == "true":
    print ''

# Set end time
toc = time.clock()

# Calculate processing time
toc - tic

# Print finishing statement
printFinish()

# Exit with return code
os._exit(returnCode)
