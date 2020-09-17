# first find ourself
fullBinPath  = os.path.abspath(os.getcwd() + "/" + sys.argv[0])
fullBasePath = os.path.dirname(os.path.dirname(fullBinPath))
fullLibPath  = os.path.join(fullBasePath, "lib")
fullCfgPath  = os.path.join(fullBasePath, "config")
sys.path.append(fullLibPath)

from origin.client import server, random_data, origin_subscriber
import ConfigParser
