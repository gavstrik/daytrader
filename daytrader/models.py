from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.conf import settings
import random
import json
import pandas as pd
names = pd.read_excel("daytrader/Fictional_Company_Names.xlsx")

author = 'Robin Engelhardt'

doc = """
In this experiment a firm is represented by a bag, containing a
variable number of 'good' and 'bad' faces. Players have to pull
out one face and guess the overall state of the firm, e.g. whether it is
in a mainly 'good' or mainly 'bad' condition. Informational cascades will
form, but since the bag (in a secondary treatment) can change
its state with a fixed probability, a mix of strategies need to be employed.
"""
#random.seed(8)

class Constants(BaseConstants):
    name_in_url = 'daytrader'
    players_per_group = None
    num_rounds = 3

    # share attributes
    num_shares = 100000
    start_price = 50.0
    start_wallet = 10000
    price_change_per_share = 0.0001

    # firm attributes
    number_of_companies = num_rounds
    # company_names = string.ascii_uppercase[:number_of_companies] # PS: change so that there can be more than 26 firms
    num_faces = 3


class Json_action:
    @staticmethod
    def from_string(bag):
        return json.loads(bag)

    @staticmethod
    def to_string(bag):
        return json.dumps(bag)


class Subsession(BaseSubsession):
    company_states = models.StringField()

    def creating_session(self):
        # creating static company states in round 1, save in session.vars
        # and retrieve for next rounds. Else we get an assignment error.
        if self.round_number == 1:
            company_names = random.sample(names["Name"].tolist(), Constants.number_of_companies)
            company_states = [[bool(random.getrandbits(1))
                                for _ in range(Constants.num_faces)]
                                for _ in range(Constants.number_of_companies)]
            self.session.vars['company_names'] = company_names
            self.session.vars['company_states'] = company_states
            for i in range(len(company_names)):
                print(i, company_names[i], company_states[i])
        else:
            company_names = self.session.vars['company_names']
            company_states = self.session.vars['company_states']


        for idp, player in enumerate(self.get_players()):
            if self.round_number == 1:
                player.wallet = Constants.start_wallet
                player.price = Constants.start_price
            player.company_name = company_names[(idp + self.round_number - 1)%Constants.num_rounds]
            player.company_state = Json_action.to_string(
                                   company_states[(idp + self.round_number - 1)%Constants.num_rounds])
            player.drawn_face = random.choice(Json_action.from_string(player.company_state))
            player.number_of_glad_faces = sum(Json_action.from_string(player.company_state))


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    wallet = models.FloatField()
    company_name = models.StringField()
    company_state = models.StringField()
    number_of_glad_faces = models.PositiveIntegerField()
    drawn_face = models.BooleanField()
    choice_of_trade = models.BooleanField(
        choices=[
            [True, 'køb (long)'],
            [False, 'lån og sælg (short)'],
        ],
        widget=widgets.RadioSelectHorizontal()
    )
    price = models.FloatField()
    price_change = models.FloatField()
    choice_of_number_of_shares = models.PositiveIntegerField(max=1000)
    can_buy = models.PositiveIntegerField()

    def choice_of_number_of_shares_max(self):
        if self.wallet <= 0.0:
            return 0
        num_shares_that_can_be_bought = int(self.wallet / self.price)
        self.can_buy = min([num_shares_that_can_be_bought, 1000])
        return self.can_buy

    def old_share_price(self):
        if self.round_number > 1:
            tmp = '{}{}'.format(self.company_name, self.round_number-1)
            return self.session.vars[tmp][0]
        else:
            return Constants.start_price

    def old_choice(self):
        if self.round_number == 1:
            return 0
        else:
            tmp = '{}{}'.format(self.company_name, self.round_number-1)
            return self.session.vars[tmp][3]

    def old_num_shares(self):
        if self.round_number == 1:
            return 0
        else:
            tmp = '{}{}'.format(self.company_name, self.round_number-1)
            return self.session.vars[tmp][4]

    def new_share_price(self):
        if self.round_number == 1:
            self.price = Constants.start_price
        else:
            price_change = 0.0

            # retrieve actions from previous round:
            tmp = '{}{}'.format(self.company_name, self.round_number-1)
            previous_choice_of_trade = self.session.vars[tmp][3]
            previous_choice_of_number_of_shares = self.session.vars[tmp][4]

            # calculate price change and add up
            if previous_choice_of_trade == True:
                price_change += Constants.price_change_per_share * previous_choice_of_number_of_shares
            else:
                price_change -= Constants.price_change_per_share * previous_choice_of_number_of_shares
            self.price = self.old_share_price() + price_change * self.old_share_price()

        return self.price

    def update_wallet(self):
        if self.round_number == 1:
            self.wallet = Constants.start_wallet
        else:
            # retrieve actions from previous round:
            previous_price = self.in_round(self.round_number - 1).price
            previous_choice_of_number_of_shares = self.in_round(self.round_number - 1).choice_of_number_of_shares
            self.wallet = self.in_round(self.round_number - 1).wallet - previous_price * previous_choice_of_number_of_shares

        return self.wallet

    def save_in_session_vars(self):
        # self.session.vars[self.company_name] = (self.drawn_face, self.choice_of_trade, self.choice_of_number_of_shares)
        tmp = '{}{}'.format(self.company_name, self.round_number)
        self.session.vars[tmp] = (self.price,
                                  self.id_in_group,
                                  self.drawn_face,
                                  self.choice_of_trade,
                                  self.choice_of_number_of_shares)
