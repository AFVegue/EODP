
# MAIN FUNCTION TO CALL THE L1C MODULE

from l1c.src.l1c import l1c

# Directory - common directory for the execution of the E2E
auxdir = r'C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP_code\\auxiliary'

# GM directory + L1B directory
#indir = (
#    r'C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP_TER_2021\\EODP_TER_2021\\EODP-TS-L1C\\input\\gm_alt100_act_150,'
#    r'C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP_TER_2021\\EODP_TER_2021\\EODP-TS-L1C\\input\\l1b_output'
#)

indir = (
    r'C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP-TS-E2E\\EODP-TS-E2E\\gm_out,'
    r'C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP-TS-E2E\\EODP-TS-E2E\\myoutput_l1b_TS'
)



# L1C output directory
#outdir = r"C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP_TER_2021\\EODP_TER_2021\\EODP-TS-L1C\\myout"
outdir = r"C:\\Users\\aleja\\OneDrive\\Escritorio\\EODP\\EODP-TS-E2E\\EODP-TS-E2E\\myoutput_l1c_TS"


# Initialise the ISM
myL1c = l1c(auxdir, indir, outdir)
myL1c.processModule()

