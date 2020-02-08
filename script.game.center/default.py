import defines
import mainform

if __name__ == "__main__":
    print "привет"
    w = mainform.WMainForm("mainform.xml", defines.SKIN_PATH, "default")
    w.doModal()
    del w