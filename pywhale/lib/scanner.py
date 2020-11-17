import os
import spf
import re
import sys


def validate_spf(from_addr, server_ip, server_mx):
    try:
        x = spf.check2(i=server_ip, s=from_addr, h=server_mx)
        if x[0] == "pass":
            return {'spf': True, 'data':x[1]}
        return {'spf': False, 'data':None}
    except Exception as e:
        return {'spf': False, 'data': str(e)}
