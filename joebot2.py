
import modules

modules.load_modules(open('data/modules.txt').readlines())

if __name__ == "__main__":
    cmd = '';
    while not cmd == 'exit':
        cmd = raw_input('>').decode('latin-1')
        modules.call_hook('message',cmd,interface=modules.console.ConsoleInterface())
