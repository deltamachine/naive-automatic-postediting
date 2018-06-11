import sys
import pipes

input_file = sys.argv[1]
output_file = sys.argv[2]
directory = sys.argv[3]
pair = sys.argv[4]

pipe = pipes.Template()
pipe.append('apertium -d ' + directory + ' ' + pair, '--')
pipe.copy(input_file, output_file)