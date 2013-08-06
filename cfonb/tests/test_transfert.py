# python import
import unittest
from datetime import date

# cfonb import
from cfonb.writer import transfert as w


def _print(res):
    print res.replace('\r\n', '\\r\\n').replace(' ', '.')


class TestTransfert(unittest.TestCase):

    def test_empty_file(self):
        d = date(2011, 10, 14)
        a = w.Transfert()
        a.setEmetteurInfos('2000121', 'bigbrother', 'virement de test', 503103, 2313033, 1212, d)
        res = a.render()
        want = open("sample_transfert_empty.cfonb", "rb").read()
        assert res == want

    def test_one_line(self):
        d = date(2011, 10, 14)
        a = w.Transfert()
        a.setEmetteurInfos('2000121', 'bigbrother', 'virement de test', 503103, 2313033, 1212, d)
        a.add('un test', 'littlebrother', 'credit agricole ile de france', 50011, 6565329000, 100, 'un peu d\'argent', 6335)
        res = a.render()
        want = open("sample_transfert_one_line.cfonb", "rb").read()
        assert res == want


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestTransfert('test_empty_file'))
    suite.addTest(TestTransfert('test_one_line'))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite())
