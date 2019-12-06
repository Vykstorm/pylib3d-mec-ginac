'''
Author: Víctor Ruiz Gómez
Description: This script is executed when jupyter loads the kernel for this library
'''


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    from lib3d_mec_ginac.ui.jupyter import JupyterClient
    IPKernelApp.launch_instance(kernel_class=JupyterClient)
