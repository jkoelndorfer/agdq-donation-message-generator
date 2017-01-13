#!/usr/bin/env python3

import functools
import random


def story_detail(func):
    func.is_story_detail = True
    cache_attr_name = "{}_".format(func.__name__)

    @functools.wraps(func)
    def wrapper(self):
        v = getattr(self, cache_attr_name, None)
        if v is None:
            v = func(self)
            setattr(self, cache_attr_name, v)
        return v
    return wrapper


class StoryTeller(object):
    def young_age(self):
        return random.choice(range(4, 14))

    def fmt_dict(self):
        attrs = (getattr(self, a) for a in dir(self))
        story_details = filter(lambda attr: getattr(attr, "is_story_detail", False) is True, attrs)
        d = {m.__name__: m() for m in story_details}
        return d

    @story_detail
    def donation_amount(self):
        return random.choice((5, 10, 15, 20, 25, 50, 75, 100))

    @story_detail
    def loss_age(self):
        return self.young_age()

    @story_detail
    def game(self):
        return random.choice((
            "Super Metroid", "Contra 3", "Super Mario Bros", "Yoshi's Island"
        ))

    @story_detail
    def native_country(self):
        return random.choice(("Germany", "Sweden"))

    @story_detail
    def extortion(self):
        return random.choice((
            "my donation message is read",
            "the runner can go the entire race without kicking someone else's console",
            "Caleb takes his shirt off and flexes for the camera"
        ))

    @story_detail
    def extortion_amount(self):
        a = random.choice((
            self.donation_amount() - 5,
            self.donation_amount() - 10,
            self.donation_amount() - 25,
            self.donation_amount() // 2
        ))
        # Minimum donation amount is $5
        if a < 5:
            a = 5

        # If the donation isn't a $5 increment, make it one.
        if a % 5 != 0:
            a = a - (a % 5)

        return a

    @story_detail
    def donation_incentive(self):
        return random.choice((
            "the {game} blindfolded run", "saving the animals",
            "killing the animals", "the {game} glitch exhibition",
            "{game} two players, one controller",
            "runner's choice", "reader's choice", "commentator's choice"
        )).format(game=self.game())

    @story_detail
    def close_person(self):
        return random.choice((
            Person("mom", "she"), Person("dad", "he"),
            Person("grandma", "she"), Person("grandpa", "he")
        ))

    @story_detail
    def close_person_relation(self):
        return self.close_person().relation

    @story_detail
    def close_person_pronoun(self):
        return self.close_person().gender_pronoun

    @story_detail
    def type_of_cancer(self):
        return random.choice((
            "breast cancer", "lung cancer", "leukemia", "melanoma"
        ))


class Person(object):
    def __init__(self, relation, gender_pronoun):
        self.relation = relation
        self.gender_pronoun = gender_pronoun


class MessageBuilder(object):
    def __init__(self):
        self.greetings_from_country = False
        self.sob_story = False
        self.extortion = False
        self.allocated_donation_incentive = False
        self.story_teller = StoryTeller()

    def m10_greeting(self):
        country_greet = "Greetings from {native_country}!"
        greet = random.choice((
            "Hey guys!", "Hey all!", "Hey AGDQ!", country_greet,
        ))
        if greet is country_greet:
            self.greetings_from_country = True
        return greet

    def m15_subgreeting(self):
        return random.choice((
            "Long time watcher, first time donator.", None
        ))

    def m20_body(self):
        sob_stories = (
            "I lost my {close_person_relation} to {type_of_cancer}.",
            "I lost my {close_person_relation} to {type_of_cancer} when I was {loss_age}.",
            "My late {close_person_relation} died to {type_of_cancer} when I was {loss_age}."
        )
        donation_incentives = (
            "Save the frames, not the animals.",
            "We're here to save lives, and that includes the animals."
        )
        bodies = [
            "I can't believe how much we have raised to fight cancer.{keep_it_up}",
            "Love watching AGDQ every year.{keep_it_up}",
            "{game} was my favorite game as kid. It's so great to see it being run at AGDQ.",
            "Watching {game} being run at AGDQ really brings me back."
        ]
        bodies.extend(sob_stories)
        bodies.extend(donation_incentives)

        b = random.choice(bodies)
        if b in sob_stories:
            self.sob_story = True
        if b in donation_incentives:
            self.allocated_donation_incentive = True
        return b

    def m25_sob_body2(self):
        if not self.sob_story:
            return None

        return random.choice((
            "AGDQ is such an awesome event.{keep_it_up}",
        ))

    def m30_donation_incentive(self):
        if self.allocated_donation_incentive:
            return None

        donation_incentives = (
            "Put my donation towards {donation_incentive}.",
            "Put my ${donation_amount} towards {donation_incentive}.",
            "Here's ${donation_amount} towards {donation_incentive}.",
            None
        )
        more_monies = (
            "I'll donate another ${extortion_amount} if {extortion}.",
            "If {extortion}, I'll donate ${extortion_amount} more.",
            None
        )
        donation_incentive = random.choice(donation_incentives)
        if donation_incentive is None:
            return None
        more_money = random.choice(more_monies)
        ret = donation_incentive
        if more_money is not None:
            self.extortion = True
            ret = ret + " " + more_money
        return ret

    def m80_closing(self):
        closings = [
            "{game} hype!", "Hype!"
        ]
        sob_closings = ["Let's kick cancer's butt."]
        sob_only_closings = ("I'm glad I am able to do my part in the fight against cancer.",)
        greetings_from_country = "Greetings from {native_country}."

        if not self.extortion:
            sob_closings.append("I wish I could donate more.")

        if not self.greetings_from_country:
            closings.append(greetings_from_country)

        closings.extend(sob_closings)
        if self.sob_story is True:
            return random.choice((*sob_closings, *sob_only_closings))
        else:
            return random.choice(closings)

    def keep_it_up(self):
        keep_it_up = random.choice((
            "Keep up the good work.", "Keep up all the great work.", "Keep up your hard work.",
            "Keep it up.", None
        ))
        # Messages don't include space around {keep_it_up}, so add a leading space (just in case it isn't included).
        if keep_it_up is not None:
            return " " + keep_it_up
        return ""

    @classmethod
    def generate(cls):
        builder = cls()
        methods = sorted((getattr(builder, m) for m in dir(builder) if m.startswith("m")), key=lambda m: m.__name__)
        msg_template = " ".join(filter(lambda x: x is not None, (m() for m in methods)))
        return msg_template.format(**builder.story_teller.fmt_dict(), keep_it_up=builder.keep_it_up())


if __name__ == "__main__":
    print(MessageBuilder.generate())
