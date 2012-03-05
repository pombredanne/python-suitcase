from pacman.fields import FieldProperty, UBInt8Sequence, UBInt8, \
    VariableRawPayload, LengthField, UBInt16
from pacman.message import BaseMessage
import unittest


class TestFieldProperty(unittest.TestCase):

    def test_basic_setget(self):
        # define the message
        class MyMessage(BaseMessage):
            _version = UBInt8Sequence(2)
            version = FieldProperty(_version,
                                    onget=lambda v: "%d.%02d" % (v[0], v[1]),
                                    onset=lambda v: tuple(int(x) for x
                                                          in v.split(".", 1)))

        msg = MyMessage()
        msg.unpack('\x10\x03')
        self.assertEqual(msg._version, (16, 3))
        self.assertEqual(msg.version, "16.03")

        msg.version = "22.7"
        self.assertEqual(msg._version, (22, 7))
        self.assertEqual(msg.version, "22.07")

class TestLengthField(unittest.TestCase):

    class MyMuiltipliedLengthMessage(BaseMessage):
        length = LengthField(UBInt8(), multiplier=8)
        payload = VariableRawPayload(length)

    class MyLengthyMessage(BaseMessage):
        length = LengthField(UBInt16())
        payload = VariableRawPayload(length)

    def test_basic_length_pack(self):
        msg = self.MyLengthyMessage()
        payload = "Hello, world!"
        msg.payload = payload
        self.assertEqual(msg.pack(), "\x00\x0DHello, world!")

    def test_basic_length_unpack(self):
        msg = self.MyLengthyMessage()
        msg.unpack('\x00\x0DHello, world!')
        self.assertEqual(msg.length, 13)
        self.assertEqual(msg.payload, "Hello, world!")

    def test_multiplied_length_pack(self):
        msg = self.MyMuiltipliedLengthMessage()
        payload = ''.join(map(chr, xrange(8 * 4)))
        msg.payload = payload
        self.assertEqual(msg.pack(), chr(4) + payload)

    def test_bad_modulus_multiplier(self):
        msg = self.MyMuiltipliedLengthMessage()
        payload = '\x01'  # 1-byte is not modulo 8
        msg.payload = payload
        self.assertRaises(ValueError, msg.pack)

    def test_multiplied_length_unpack(self):
        msg = self.MyMuiltipliedLengthMessage()
        msg.unpack(chr(4) + ''.join([chr(x) for x in xrange(8 * 4)]))
        self.assertEqual(msg.length, 4)
        self.assertEqual(msg.payload,
                         ''.join([chr(x) for x in xrange(8 * 4)]))


class TestByteSequence(unittest.TestCase):

    def test_bubyte_sequence(self):
        class MySeqMessage(BaseMessage):
            type = UBInt8()
            byte_values = UBInt8Sequence(16)

        msg = MySeqMessage()
        msg.type = 0
        msg.byte_values = (0, 1, 2, 3, 4, 5, 6, 7, 8,
                           9, 10, 11, 12, 13, 14, 15)
        self.assertEqual(msg.pack(),
                         '\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08'
                         '\t\n\x0b\x0c\r\x0e\x0f')

if __name__ == "__main__":
    unittest.main()
