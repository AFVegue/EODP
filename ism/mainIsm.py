
# MAIN FUNCTION TO CALL THE ISM MODULE

from ism.src.ism import ism

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP_code\\auxiliary'
#indir = r"C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP_TER_2021\\EODP_TER_2021\\EODP-TS-ISM\input\gradient_alt100_act150"
indir = r"C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP-TS-E2E\\EODP-TS-E2E\\sgm_out"
#outdir = r"C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP_TER_2021\\EODP_TER_2021\\EODP-TS-ISM\myoutput"
outdir = r"C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP-TS-E2E\\EODP-TS-E2E\\myoutput_TS"

# Initialise the ISM
myIsm = ism(auxdir, indir, outdir)
myIsm.processModule()
