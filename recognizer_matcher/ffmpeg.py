import subprocess as sp
import sys


def server_open(output_file, frame_x, frame_y, fps):
    try:
        dimension = '{}x{}'.format(frame_x, frame_y)
        output_file = output_file
        command = ['ffmpeg', '-y', '-nostats', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-s', dimension, '-pix_fmt', 'bgr24', '-r',
                   str(fps), '-i', '-', '-an', '-vcodec', 'mpeg4', '-b:v', '5000k', output_file]
        proc = sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE)
        return False, proc
    except OSError as e:
        print("OSError > ", e.errno)
        print("OSError > ", e.strerror)
        print("OSError > ", e.filename)
        return True, None
    except Exception:
        print("Error > ", sys.exc_info()[0])
        return True, None
