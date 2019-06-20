import  os
if __name__ == '__main__':
    from PyInstaller.__main__ import run
    opts=['main.py','-c',"-y","-F"]
    run(opts)