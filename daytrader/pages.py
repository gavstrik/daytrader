from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class Intro1(Page):
    def is_displayed(self):
        return self.round_number == 1


class Intro2(Page):
    def is_displayed(self):
        return self.round_number == 1


class Intro3(Page):
    def is_displayed(self):
        return self.round_number == 1


class Intro4(Page):
    def is_displayed(self):
        return self.round_number == 1


class Intro5(Page):
    def is_displayed(self):
        return self.round_number == 1


class MyWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for player in self.group.get_players():
            player.new_share_price()
            player.update_wallet()
            player.choice_of_number_of_shares_max()


class Choose(Page):
    form_model = 'player' # setting a form model for current player
    form_fields = ['choice_of_trade', 'choice_of_number_of_shares'] # setting a form field to fill out

    timeout_seconds = 20
    # retrieving variables for a trade history table
    def vars_for_template(self):
        prices = [self.session.vars['{}{}'.format(self.player.company_name, r)][0]
                    for r in range(1, self.player.round_number)]
        choices = [self.session.vars['{}{}'.format(self.player.company_name, r)][3]
                    for r in range(1, self.round_number)]
        deals = [self.session.vars['{}{}'.format(self.player.company_name, r)][4]
                    for r in range(1, self.player.round_number)]
        rounds = [r for r in range(1, self.player.round_number)]
        data = zip(rounds, prices, choices, deals)

        return {
           'data': data,
        }


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for player in self.group.get_players():
            player.save_in_session_vars()


class Delisted(Page):
    def is_displayed(self):
        return self.player.price < 1

    def vars_for_template(self):
        return {
            'max_minus': -Constants.max_borrow
        }


class Results(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        self.player.payoff()
        return {
            'wallet': c(self.player.wallet - self.player.price * self.player.choice_of_number_of_shares),
        }


page_sequence = [
    Intro1,
    Intro2,
    Intro3,
    Intro4,
    Intro5,
    MyWaitPage,
    Choose,
    ResultsWaitPage,
    Delisted,
    Results
]
