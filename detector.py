import numpy as np
import cv2

baseball_cascade = cv2.CascadeClassifier('baseball.xml')
basketball_cascade = cv2.CascadeClassifier('basketball.xml')
tennis_cascade = cv2.CascadeClassifier('tennis.xml')

# testfile = 'satellite/training/pitch_baseball_220727025.png'
# testfile = 'satellite/training/pitch_baseball_222703638.png'
# testfile = 'satellite/training/pitch_baseball_223914194.png'
# testfile = 'satellite/training/pitch_baseball_226905824.png'
# testfile = 'satellite/training/pitch_baseball_227372226.png'
# testfile = 'satellite/training/pitch_baseball_227683244.png'

# testfile = 'satellite/detection/pitch_baseball_133230978.png'
# testfile = 'satellite/detection/pitch_baseball_133593974.png'
# testfile = 'satellite/detection/pitch_baseball_134874855.png'
# testfile = 'satellite/detection/pitch_baseball_199130202.png'
# testfile = 'satellite/detection/pitch_baseball_284527697.png'
# testfile = 'satellite/detection/pitch_baseball_317137177.png'
# testfile = 'satellite/detection/pitch_baseball_48331085.png'
# testfile = 'satellite/detection/pitch_baseball_68467399.png'
# testfile = 'satellite/detection/pitch_baseball_81189377.png'
# testfile = 'satellite/detection/pitch_baseball_97575184.png'

# testfile = 'satellite/detection/pitch_tennis_105660674.png'
# testfile = 'satellite/detection/pitch_tennis_120231577.png'
# testfile = 'satellite/detection/pitch_tennis_172547292.png'
# testfile = 'satellite/detection/pitch_tennis_177425633.png'
# testfile = 'satellite/detection/pitch_tennis_224740547.png'
# testfile = 'satellite/detection/pitch_tennis_250911604.png'
# testfile = 'satellite/detection/pitch_tennis_285058169.png'
# testfile = 'satellite/detection/pitch_tennis_290182837.png'
# testfile = 'satellite/detection/pitch_tennis_302813940.png'
# testfile = 'satellite/detection/pitch_tennis_343232913.png'

# testfile = 'satellite/detection/pitch_basketball_139165791.png'
# testfile = 'satellite/detection/pitch_basketball_156416713.png'
testfile = 'satellite/detection/pitch_basketball_242894925.png'
# testfile = 'satellite/detection/pitch_basketball_256427642.png'
# testfile = 'satellite/detection/pitch_basketball_271825251.png'
# testfile = 'satellite/detection/pitch_basketball_276916820.png'
# testfile = 'satellite/detection/pitch_basketball_302422677.png'
# testfile = 'satellite/detection/pitch_basketball_331162643.png'
# testfile = 'satellite/detection/pitch_basketball_332627356.png'
# testfile = 'satellite/detection/pitch_basketball_48665083.png'

img = cv2.imread(testfile)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

pitches = basketball_cascade.detectMultiScale(gray, minNeighbors=200)
print 'Pitches found: %d' % len(pitches)
for (x,y,w,h) in pitches:
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
