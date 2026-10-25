import pexpect
import sys
import time

child = pexpect.spawn('tail -f workflow_gpu_2.log', encoding='utf-8')
try:
    child.expect('=== 結合計算が正常に完了しました ===', timeout=120)
    print("FINISHED")
except pexpect.TIMEOUT:
    print("TIMEOUT - output so far:")
    print(child.before)
