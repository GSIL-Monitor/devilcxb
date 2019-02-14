from random import Random
import copy


class RandomBankCard(object):
    def __init__(self):
        self.visaPrefixList = [
            ['4', '5', '3', '9'],
            ['4', '5', '5', '6'],
            ['4', '9', '1', '6'],
            ['4', '5', '3', '2'],
            ['4', '9', '2', '9'],
            ['4', '0', '2', '4', '0', '0', '7', '1'],
            ['4', '4', '8', '6'],
            ['4', '7', '1', '6'],
            ['4']]
        self.mastercardPrefixList = [
            ['5', '1'], ['5', '2'], ['5', '3'], ['5', '4'], ['5', '5']]
        self.amexPrefixList = [['3', '4'], ['3', '7']]
        self.discoverPrefixList = [['6', '0', '1', '1']]
        self.dinersPrefixList = [
            ['3', '0', '0'],
            ['3', '0', '1'],
            ['3', '0', '2'],
            ['3', '0', '3'],
            ['3', '6'],
            ['3', '8']]
        self.enRoutePrefixList = [['2', '0', '1', '4'], ['2', '1', '4', '9']]
        self.jcbPrefixList = [['3', '5']]
        self.voyagerPrefixList = [['8', '6', '9', '9']]
        self.debitrefixList = [[['6', '2', '2', '5', '8', '0'], 16],
                               [['6', '2', '2', '5', '8', '8'], 16],
                               [['6', '2', '2', '5', '9', '8'], 16],
                               [['6', '2', '2', '6', '1', '5'], 16],
                               [['6', '2', '2', '6', '1', '7'], 16],
                               [['6', '2', '2', '6', '1', '9'], 16],
                               [['6', '2', '2', '6', '2', '2'], 16],
                               [['6', '2', '2', '6', '3', '0'], 16],
                               [['6', '2', '2', '6', '3', '1'], 16],
                               [['6', '2', '2', '6', '3', '2'], 16],
                               [['6', '2', '2', '6', '3', '3'], 16],
                               [['6', '2', '2', '6', '6', '0'], 16],
                               [['6', '2', '2', '6', '9', '8'], 16],
                               [['6', '2', '2', '7', '0', '0'], 19],
                               [['6', '2', '2', '8', '2', '1'], 19],
                               [['6', '2', '2', '8', '2', '2'], 19],
                               [['6', '2', '2', '8', '2', '3'], 19],
                               [['6', '2', '2', '8', '2', '4'], 19],
                               [['6', '2', '2', '8', '2', '5'], 19],
                               [['6', '2', '2', '8', '2', '6'], 19],
                               [['6', '2', '2', '8', '4', '0'], 19],
                               [['6', '2', '2', '8', '4', '4'], 19],
                               [['6', '2', '2', '8', '4', '5'], 19],
                               [['6', '2', '2', '8', '4', '6'], 19],
                               [['6', '2', '2', '8', '4', '7'], 19],
                               [['6', '2', '2', '8', '4', '8'], 19],
                               [['6', '9', '0', '7', '5', '5'], 15],
                               [['6', '9', '0', '7', '5', '5'], 18]]

    def completed_number(self, prefix, length):
        """
        'prefix' is the start of the CC number as a string, any number of digits.
        'length' is the length of the CC number to generate. Typically 13 or 16
        """
        ccnumber = prefix
        # generate digits
        generator = Random()
        generator.seed()  # Seed from current time
        while len(ccnumber) < (length - 1):
            digit = str(generator.choice(range(0, 10)))
            ccnumber.append(digit)
        # Calculate sum
        sum = 0
        pos = 0
        reversedCCnumber = []
        reversedCCnumber.extend(ccnumber)
        reversedCCnumber.reverse()
        while pos < length - 1:
            odd = int(reversedCCnumber[pos]) * 2
            if odd > 9:
                odd -= 9
            sum += odd
            if pos != (length - 2):
                sum += int(reversedCCnumber[pos + 1])
            pos += 2
        # Calculate check digit
        checkdigit = ((sum / 10 + 1) * 10 - sum) % 10
        ccnumber.append(str(checkdigit))
        return ''.join(ccnumber)

    def credit_card_number(self, prefixList, length=None, howMany=1):
        generator = Random()
        generator.seed()  # Seed from current time
        result = []
        while len(result) < howMany:
            ccnumber = copy.copy(generator.choice(prefixList))
            if prefixList == self.debitrefixList:
                length = ccnumber[1]
                ccnumber = ccnumber[0]
            result.append(self.completed_number(ccnumber, length))
        return result

    def output(self, title, numbers):
        result = []
        result.append(title)
        result.append('-' * len(title))
        result.append('\n'.join(numbers))
        result.append('')
        return '\n'.join(result)


if __name__ == '__main__':
    RandomBankCard = RandomBankCard()
    # print("darkcoding credit card generator\n")
    # mastercard = RandomBankCard.credit_card_number(RandomBankCard.mastercardPrefixList, 16, 10)
    # print(RandomBankCard.output("Mastercard", mastercard))
    # visa16 = RandomBankCard.credit_card_number(RandomBankCard.visaPrefixList, 16, 1)
    # print(RandomBankCard.output("VISA 16 digit", visa16))
    # visa13 = RandomBankCard.credit_card_number(RandomBankCard.visaPrefixList, 13, 5)
    # print(RandomBankCard.output("VISA 13 digit", visa13))
    # amex = RandomBankCard.credit_card_number(RandomBankCard.amexPrefixList, 15, 5)
    # print(RandomBankCard.output("American Express", amex))
    # # Minor cards
    # discover = RandomBankCard.credit_card_number(RandomBankCard.discoverPrefixList, 16, 3)
    # print(RandomBankCard.output("Discover", discover))
    # diners = RandomBankCard.credit_card_number(RandomBankCard.dinersPrefixList, 14, 3)
    # print(RandomBankCard.output("Diners Club / Carte Blanche", diners))
    # enRoute = RandomBankCard.credit_card_number(RandomBankCard.enRoutePrefixList, 15, 3)
    # print(RandomBankCard.output("enRoute", enRoute))
    # jcb = RandomBankCard.credit_card_number(RandomBankCard.jcbPrefixList, 16, 3)
    # print(RandomBankCard.output("JCB", jcb))
    # voyager = RandomBankCard.credit_card_number(RandomBankCard.voyagerPrefixList, 15, 3)
    # print(RandomBankCard.output("Voyager", voyager))
    debit = RandomBankCard.credit_card_number(RandomBankCard.debitrefixList, howMany=2)
    print(RandomBankCard.output("Debit", debit)).strip()
    print "-----"
