import json, sys, os
from pathlib import Path
from paths import DATA, SITE, SRC

ents = json.load(open(DATA / "ents.json"))
ents["amazon"][6] = max(ents["amazon"][6], 1)  # "Ama zon.com" split by PDF extraction in Dec 2004
totals = json.load(open(DATA / "totals.json"))["totals"]
words = open(DATA / "wordindex.txt").read()

def per(y, m):
    if m == "06": return f"Six months to 30 June {y}"
    return f"Year to 31 December {y}"

L = []
def letter(id, title, ret, idx, summary, points, story, distinct, retNote=None, quote=None, quoteBy=None, period=None):
    y, m = id.split("-")
    L.append(dict(id=id, title=title, ret=ret, idx=idx, retNote=retNote, summary=summary, points=points, story=story,
                  distinct=distinct, quote=quote, quoteBy=quoteBy, period=period or per(y, m)))

letter("2001-12", "Launching into a falling market", 10.1, 3.6,
 "Nomad bought its first shares on 10 September 2001, the day before 9/11. Markets fell almost at once, so the money went to work faster, and more cheaply, than planned. This first letter sets out what Nick Sleep is looking for: businesses priced at about half their real value, run by owner-minded managers who allocate capital well. A global mandate, he argues, makes that rare combination easier to find. Two early holdings show the type. International Speedway had bought up NASCAR tracks, which strengthened its hand with TV networks. Matichon, a debt-free Thai newspaper, was priced at a fraction of its worth and paid a hefty dividend. About 28% of the fund was still in cash.",
 ["Aim for roughly 50 cents on the dollar, owner-oriented managers and sound capital allocation.",
  "A global remit widens the search, and nothing has to be owned.",
  "Frequent reporting would be of little use to partners and might harm the managers.",
  "The early tilt was to media, hotels and casinos, and telecoms, with a third of the fund in Southeast Asia."],
 "Nobody at Nomad could read Thai, so the verdict on Matichon’s editorial stance came from Thai friends.",
 ["nascar","circuits","speedway","matichon","thai","racing"], period="10 September – 31 December 2001")

letter("2002-06", "Xerox, and an honest error", 3.99, -8.60,
 "Drawing on Buffett’s early partnership letters, Sleep tells partners to expect Nomad to shine when markets fall and to do no better than average when they boom. He explains why short horizons create bargains: a professional judged on this year’s results may pass on a share he knows will soar next January. The portfolio is sorted into three buckets (hard-to-copy franchises, asset-backed discounts and deep-value workouts) and, by Nomad’s estimate, priced at 51 cents on the dollar. Xerox gets a patient tour of lease accounting. Its restatement moved profits between years but left cash flow alone, and the shares traded below half of Nomad’s valuation. Monsanto is the confessed error. Nomad missed an indemnity for a former subsidiary’s pollution liabilities, buried in the notes to the accounts, and sold the shares at about cost.",
 ["Expect to outperform in falling markets, not every year.",
  "Short-term incentives stop professionals buying obvious long-term bargains.",
  "Value rests on cash flow, not reported earnings.",
  "Name the mistakes: the manager is fallible."],
 "A fellow investor’s thought experiment: you know for certain that a share will rise tenfold next January. You would buy today. A manager who must beat the market this quarter has no use for it.",
 ["lease","xerox","monsanto","solutia","attention","damages"])

letter("2002-12", "A bus company and a warehouse club", 1.3, -19.9,
 "Nomad made a small gain in 2002 while the index fell by a fifth. Conseco’s bankruptcy stays on the list of holdings, because Sleep won’t tidy mistakes away. With investors at their most frightened in late 2002, cash fell from over 20% of the fund to about 5%, and nearly half the companies owned were buying back shares or debt. Two new holdings lead the letter. Stagecoach, the British bus operator, had crippled itself with a debt-funded American acquisition. Its founder was back to cut away the weak parts, and Nomad bought at 14p against a 60p appraisal, making it the largest position. Costco needed no fixing. A membership fee plus a fixed, low mark-up makes a simple bargain with shoppers, and the savings from its scale flow back into lower prices.",
 ["These results were earned without leverage, shorting or derivatives.",
  "Fear, not fundamentals, set prices in late 2002.",
  "Cut a troubled company back to its ‘jewel’.",
  "Costco’s fixed mark-up turns savings into growth."],
 "Costco once sourced designer jeans cheaply enough to take a far fatter margin. Jim Sinegal refused, reasoning that one exception would become a habit.",
 ["souter","bus","georgica","jewel","deregulation","plates"])

letter("2003-06", "The widest possible mandate", 26.0, 11.1,
 "Partners voted unanimously to let Nomad own unlisted shares, and it promptly bought Weetabix. The family-run British cereal maker traded on the obscure Ofex market, and Nomad paid about £20 a share against an estimated worth of £70. A screen for US companies whose share count hadn’t moved in ten years found only a handful, including Erie Family Life and the charmingly unhelpful Hershey Creamery. Sleep argues that narrow mandates stop most managers from buying whatever is cheapest. Nomad can hold preferred shares, bonds, unlisted equity and anything in between, and that freedom is the reason for its name. Lucent’s 8% preferred shares, bought far below par, had tripled. And Nomad had turned away almost as much money as it accepted.",
 ["Per-share discipline matters: steady share issuance quietly dilutes owners.",
  "A broad mandate is an edge in its own right.",
  "Brands grow when their share of advertising exceeds their share of the market.",
  "Recycle winners into new fifty-cent dollars."],
 "Asked for an annual report, Hershey Creamery’s finance chief said reports go only to shareholders, and conceded that this was a common complaint.",
 ["weetabix","prefs","lucent","erie","ofex","issuance"])

letter("2003-12", "How the fifty-cent dollar works", 79.6, 33.1,
 "A dollar had doubled in just over two years, but Sleep declines the credit. Most of the gain came from fear draining out of the most hated stocks as companies like Stagecoach repaired their balance sheets. He then lays out the arithmetic behind the approach. Buy at 50 cents, let the business’s value grow about 10% a year, and a winner compounds at roughly 26%. If half the portfolio merely stagnates, the whole still makes about 13%. New subscriptions, he admits, drive him mad because they dilute the winners. He would rather match new money to new ideas, and close before long. Finally, Hicks Muse is taking Weetabix private at a price Nomad thinks too low. Nomad voted against the deal and lost.",
 ["Judge results over five years, compounded, not year by year.",
  "Winners add more to returns than losers take away.",
  "Price and management’s capital allocation decide the outcome.",
  "Own more than 10% of a company if you want a say."],
 "A partner said his wife treated Nomad’s gains as future jewellery. Sleep offered no advice, only Buffett’s remark that he had never regretted a jewellery purchase.",
 ["hicks","muse","jewelry","darwin","scheme","subscriptions"])

letter("2004-06", "Closed, concentrated, and a list of great thinkers", -0.97, 3.52,
 "After drawing down its waiting list, Nomad reached about $100m and closed to new money, meaning to reopen only when markets offered bargains. About a third of the fund was in Southeast Asia, and the portfolio was priced at roughly 61 cents on the dollar. Union Cement shows the cost of price discipline. It traded at a quarter of replacement cost but so rarely that Nomad bought only a sliver before Holcim paid five times Nomad’s average price. Sleep cites the Kelly criterion to argue that Nomad has been too diversified. He thanks fellow shareholders who fought for value at Jardine, Kersaf and Hollinger. And he describes an office list of ‘super-high-quality thinkers’, the ‘terminal portfolio’ he hopes to own once prices allow.",
 ["Grow when prices are depressed, not at market tops.",
  "If you are confident, bet big. Over-diversification is a comfort blanket.",
  "Large, engaged owners improve how companies behave.",
  "Good companies behave well because they want to, not because they have to."],
 "Union Cement’s shares traded so rarely that the implied holding period was over 40 years, about the life of a cement plant.",
 ["cement","union","closet","kelly","thinkers","allocation"])

letter("2004-12", "Deconstructing Costco", 22.1, 14.7,
 "Sleep calls the growth-versus-value debate unnecessary. A business is worth its future free cash flow, so growth is part of value, and popular valuation ratios are shortcuts that reveal little. Most of the letter dissects Costco, now close to a tenth of Nomad. It caps its mark-up, stocks about 4,000 carefully chosen products, expects suppliers to quote their lowest price, and hands the savings from its scale back to customers. Sleep names the model ‘scale efficiencies shared’. Working through the numbers, he finds that older warehouses earn far more than new ones, so profits should rise as the store base matures, and he concludes that the position is too small. He also floats eBay as a candidate for the most valuable business in the world.",
 ["See a company as a compounding machine, not a static balance sheet.",
  "Ask a value investor what stopped them owning K-Mart, and a growth investor what stopped them selling Wal-Mart.",
  "Thin margins can be a deliberate strategy.",
  "Talking up a holding in public can lock you into it."],
 "Curious about Zimbabwe, the team asked a mining giant to arrange a meeting with its local subsidiary. Its investor relations officer asked whether that subsidiary was even listed.",
 ["costco","heuristics","dell","stores","ebay","mark-up"])

letter("2005-06", "Measuring the moat", 2.4, -0.3,
 "Nomad rose only 2% in six months, but its price-to-value ratio fell from the low 70s to the upper 60s, which Sleep says matters more. He adopts Bill Miller’s three possible edges (information, analysis and behaviour) and places Nomad’s edge in behaviour, shared with patient partners. He introduces the ‘robustness ratio’, comparing what customers save with what shareholders earn: about 1:1 at GEICO and about 5:1 at Costco. A second investment model appears, deep discounts to replacement cost with latent pricing power. Zimbabwe is the example: a cement maker there traded at a seventieth of replacement cost. Sleep explains that Nomad values those shares using an exchange rate implied by Old Mutual’s share price in Harare and Johannesburg, close to the street rate, rather than the official rate. And he drops two cherished rules, since a low share price and high insider ownership aren’t always good.",
 ["The price-to-value ratio is the scorecard, not the share price.",
  "Investors can profit because fewer things happen than could.",
  "The 6% hurdle reflects the risk of losing money.",
  "Take away rules and people may think harder."],
 "Floods in Carlisle knocked out the traffic lights at a seven-road junction. Traffic moved faster without them, and apparently more safely.",
 ["robustness","geico","cardholder","cement","zimbabwe","division"])

letter("2005-12", "Four ways to misjudge", 9.2, 9.5,
 "Five years in, a dollar has become about $2.67 before fees. Sleep credits timing: Nomad launched into the aftermath of the Asian and junk-bond crises. He warns that 25% a year is unlikely without more distress. He asks how partners would feel if Nomad handed back money when opportunities dried up. He also proposes a high-water mark that rises 6% a year, so that no ‘performance’ fee is earned on returns a deposit account could match. The core of the letter lists four causes of misjudgement: social proof, availability, weak probabilistic thinking and impatience. Institutions that sold Matichon for business reasons rather than on value illustrate them. The goal is stated: turn $1 into $16 over twenty years. Sleep’s speech to The Investment Fund for Foundations (TIFF), on why the approach worked so well in Asia, is attached.",
 ["The destination matters more than the order of the returns.",
  "Fund size should flex with opportunity, even shrinking.",
  "Think like a principal, not an agent.",
  "Selling a future ten-bagger costs more than owning a company that goes bankrupt (from the speech)."],
 "Sleep spent a year tracking down Richard Zeckhauser to learn what Munger meant about how he plays bridge. The answer: he uses decision trees with probabilities attached and updates them as the facts change.",
 ["probabilities","bridge","zeckhauser","geography","disease","proof"])

letter("2006-06", "Going independent", 3.2, 6.1,
 "Sleep and Zakaria have left Marathon to set up Sleep, Zakaria and Company, which takes over Nomad in September 2006. This time the performance figures were sent separately. The letter recounts the hunt for administrators willing to handle a refundable performance fee, a four-week regulatory approval, and the rules for any reopening: existing partners first, then principals ahead of agents. The target is to turn $1 into $10 within a decade. Non-transitive dice show why any edge only becomes visible over time. Sleep points to frantic trading in commodity shares, where Phelps Dodge owners held for three months on average. He suggests the neglected corner of the market is now large, high-quality growth companies. The April 2006 letter attached explains the thinking behind the proposed new fees.",
 ["A management fee should cover costs, not make a profit.",
  "Performance fees should stay at risk in case results later disappoint.",
  "Very short holding periods are a sign of speculation.",
  "The new firm is structured so that Nomad can never be sold to another manager."],
 "The regulator assumed Nomad had left some zeros off its reported three trades a month.",
 ["dice","blenkinsopp","prospectus","handover","cookie","non-transitive"],
 retNote="Derived from later tables; performance was sent separately")

letter("2006-12", "The long end of the equity yield curve", 13.6, 20.1,
 "The first year-end letter from the new firm, which they call ‘Galactic HQ’. Nomad trailed the index, and Sleep says the index is just one opportunity set, not a risk-free home. He sets out the ‘equity yield curve’. Businesses are more predictable over five years than over five months, so patience earns more, and Nomad’s longer-held stocks had indeed earned higher annual returns. Others hold Nomad’s stocks for about 20 weeks; Nomad expects to hold them for 260. Amazon is the case study: growth spending and price cuts depress today’s cash flow, and traders ignore Bezos’s explanation of why. The top five holdings make up half the fund. Sleep also attacks cheap take-privates and describes Nomad’s stakes in Games Workshop, Jarvis and Whitehead Mann.",
 ["The index isn’t risk-free.",
  "Time can raise returns and lower risk.",
  "Unconstrained investors should earn more than boxed-in ones.",
  "Own enough to block low-ball takeovers."],
 "Friends looked at the firm’s homespun website and asked whether that was really what they wanted. It was: the fancy stuff could be left to Amazon.",
 ["curve","cpr","givebacks","compulsory","bucket","racing"])

letter("2007-06", "Mice, elephants and Amazon", 17.6, 9.2,
 "A dollar is now worth $3.58. Sleep warns against extrapolating, and explains why long-term investors must work harder at honesty: the brain learns from instant feedback, and investment results arrive years late. Through the Santa Fe Institute he borrows Geoffrey West’s scaling laws (mammals get roughly a billion heartbeats) and asks what lets a company grow from mouse to elephant. His answer is self-funded growth and a simple skeleton that gets stronger with size. Online retail fits, and Amazon is now a sixth of Nomad. Selling it could repeat the error of selling Wal-Mart early; Nomad’s own worst mistake so far was selling Stagecoach. Over 85% of the fund is in founder-run companies, which they had not planned.",
 ["Build a portfolio down from 100%, not up from 1%.",
  "Errors of omission cost more than bankruptcies.",
  "The market’s deep reality is founders on one side and quarterly traders on the other.",
  "Future capital could be raised in shares that can later be redeemed."],
 "Oil was found underneath Exxon’s own headquarters, and not by Exxon.",
 ["skeletal","heartbeats","mouse","scaling","exxon","animals"])

letter("2007-12", "A letter about mistakes", 21.2, 9.0,
 "This letter is about mistakes. Sleep argues for learning without judgement, since a mistake whose lesson is absorbed can end up paying for itself. He contrasts MDC, a homebuilder that learned from the early-1990s bust, with an unnamed European bank that drew the wrong lesson and diversified. Nomad’s own big errors, Conseco and selling Stagecoach too soon, came from a view of the business frozen at the time of purchase. The fix was ‘destination analysis’, which he credits with keeping Nomad out of US banks and in Amazon during 2007. He names denial, anchoring and drift as traps and wonders whether managers say too much. He asks partners to judge the inputs Nomad can control rather than its annual results.",
 ["How you respond to a mistake matters more than the mistake.",
  "Diversification can turn ignorance into false comfort.",
  "Measure errors by what they cost in missed opportunity.",
  "Share-price volatility is not investment risk."],
 "Buffett reportedly turned down a bet that cost $10 and would have paid $10,000 for a hole-in-one. Small lapses in discipline, he said, lead to big ones.",
 ["mistakes","learnt","walter","ignatius","rockefeller","lockhart"])

letter("2008-06", "Wrong, quickly: AirAsia, Games Workshop, MBIA", -20.8, -10.6,
 "Nomad fell about 20% in six months, and the performance fee held in reserve was refunded to partners. Sleep walks through three purchases that went ‘wrong’ quickly. AirAsia, perhaps the world’s lowest-cost airline, was priced below the value of its planes. Games Workshop, whose chairman bluntly blamed the company’s own complacency, was valued at little more than its equipment. MBIA, the bond insurer, was sold because the chance of heavy share issuance at low prices made its value per share unknowable, a worked lesson in dilution risk. Businesses that share their scale economies with customers now make up about 45% of the fund. Holders of Nomad’s US stocks keep them for 51 days on average, and that gap, Sleep says, is the whole investment case.",
 ["Dilution risk peaks at market lows.",
  "Large holders who underwrite rights issues can remove it.",
  "Momentum markets chase what has already risen.",
  "Nearly 90% of the fund is in firms run by their founders or largest shareholders."],
 "At the Savoy hotel auction, Sleep bid for a chrome ‘S’ (S for Savoy, S for Sleep). He admits he bought on the final day, after prices had risen every day.",
 ["dilution","southwest","mbia","games","savoy","shorts"])

letter("2008-12", "The case for slack", -45.3, -40.7,
 "It was a brutal year: Nomad lost 45%, and five-year returns were roughly zero. Sleep asks partners to look instead at the widening gap between price and value. The crisis, he argues, exposed a world optimised to the last dollar, with no slack: over-geared banks, over-filled diaries. Cash waiting for a better opportunity is worth more than its interest rate. He contrasts the incentives in high-low retailing with those in scale economics shared. He estimates that Amazon could quadruple its US sales by winning a tenth of what struggling high-street rivals sell, and notes that its holiday orders rose while US retail sales fell. Nomad reopened to new money, with the founders among its largest subscribers. The Zimbabwe holdings were written down to zero after trading there stopped.",
 ["Be right, not busy.",
  "Incentives shape behaviour, in schools as in companies.",
  "Watch price-to-value, not performance.",
  "Crises are when future gains are loaded."],
 "A collector bought both James Bond Aston Martins for £1,500, then swapped one for a Ferrari 250 GTO. That made his GTO effectively a £750 car, and he kept it.",
 ["slack","busy","gto","norway","incentives","aston"],
 quote="Zak and I don’t want to be busy; we want to be right.", quoteBy="Nick Sleep, letter for 2008")

letter("2009-06", "Whispered truths", 20.9, 6.4,
 "Opening with Darwin’s modest introduction to <i>On the Origin of Species</i>, Sleep observes that true things are often said quietly. About two-thirds of Nomad is in companies that avoid self-promotion: no advertising, no earnings guidance, savings handed back to customers as lower prices. Amazon’s revenue grew more than 60% after the credit crisis began, while its share price lurched. Sleep challenges the orthodoxy of diversification, pointing out that great fortunes were built in a single company. He uses Wal-Mart to show that great businesses can stay undervalued for decades because investors misweigh lasting advantages. Scale economics shared is now over half the fund. Ten holdings make up about 80% of it, and one about 30%. Partners added money during the crisis.",
 ["Share prices are more volatile than business values.",
  "Owning more stocks can raise risk.",
  "The market underrates how long compounding can last.",
  "Not acting is a decision too."],
 "A large fund firm sold its IBM stake and, later, its Wal-Mart stake. Each would eventually have been worth more than all the money the firm managed.",
 ["darwin","knowable","wal-mart","walton","shouting","culture"])

letter("2009-12", "Investment heaven", 71.5, 30.0,
 "A dollar has become $2.90 after every fee, against $1.40 in the index. Sleep credits partners twice. Voting to delist from the Irish exchange let Nomad take bigger positions, which added about 20% to net asset value. Staying invested after the 2008 crash, rather than redeeming, earned about 70% in 2009. He attacks the ‘locker room culture’ of winning at any cost, and cites an unnamed founder on being willing to be misunderstood and working backwards from the customer. By his estimate, fewer than one listed company in twenty does what’s right rather than what plays well. His key insight is character. Owning businesses of great character, and not fiddling with the portfolio, cuts the risk of reinvesting badly. He calls the result investment heaven.",
 ["The companies, not the managers, create the wealth.",
  "Companies get the investors they deserve, and investors get the companies they deserve.",
  "Character may be all that matters in the long run.",
  "They are drifting toward inactivity, on purpose."],
 "The letter’s disclaimer borrows the motto reportedly displayed at an Indian railway ticket kiosk: ‘No Bamboozlement Here’.",
 ["locker","room","misunderstood","salesman","character","mindset"])

letter("2010-06", "Many small things", -2.7, -9.8,
 "A visit to a Welsh motor insurer upends one of Sleep’s old assumptions: its advantage came not from one big idea but from doing many things slightly better. Costco’s low costs likewise come from thousands of daily decisions. Jim Sinegal gave them a copy of a 1967 memo by Sol Price about bringing goods to people as cheaply as possible, and it now hangs framed on their wall. Amazon sets hundreds of detailed goals each year. A company built on one big thing, such as a drug patent, is fragile; one built on countless small advantages is hard to copy. Borrowing Ole Peters’ point that a company travels down one branch of the future at a time, Sleep argues that for firms like AirAsia each success raises the odds of the next, and share prices fail to reflect this.",
 ["Culture compounds.",
  "Don’t go looking only for a smoking gun; that is a framing error.",
  "Share prices miss odds that improve along the way.",
  "Partners’ patience completes the ecosystem."],
 "One Amazon employee suggested removing the light bulbs from vending machines. It saves $20,000 a year.",
 ["branch","drug","insurance","welsh","smoking","gun"])

letter("2011-06", "Habits, not warehouses", 17.5, 6.3,
 "Before fees, $1 has become $5.87. Sleep examines mental shortcuts. One panellist dismissed a cheap Zimbabwe investment on sight. Car buyers read the adverts after choosing, to justify the decision. He asks why online retailers grow no faster than physical retailers once did, even though they have no shelf-space or opening-hour limits. His hunch is that growth is set by how quickly shoppers drop old habits. If so, large online retailers can still be young, and forecasts that assume growth starts fading today will be badly wrong. He regrets that rules have replaced trust in the investment industry. And he marks ten years of Nomad, five of the firm, and twenty in the business for each partner.",
 ["A bad association can block a good idea.",
  "Don’t assume regression to the mean starts today.",
  "Rules have replaced trust in fund management.",
  "Rebuild a web of deserved trust."],
 "The bees on the office roof produced a bumper honey harvest.",
 ["panelist","online","retailing","hunch","internet","celebrate"])

letter("2011-12", "Cash in, cash out", -9.9, -5.5,
 "Early in his career, a bank’s finance chief told Sleep that everything comes down to cash in and cash out, and the lesson stuck. Nomad is now, for practical purposes, ten companies. To filter out noise, the test is whether a piece of news changes a company’s bond with its customers. Bezos describes two routes to success: persuade customers to pay high margins, or work hard to offer low ones. Nomad’s firms are in the second camp. They are growing revenues over 30% a year without acquisitions, and earn returns on capital about twice their rivals’. The real risks, Sleep argues, aren’t the headlines. They are a dishonest response to a problem, bubble valuations, or a political backlash such as an online sales tax. A failed school, turned around on the same budget, shows that choices count for more than money.",
 ["Keep it simple: cash in, cash out.",
  "Give the most weight to the customer relationship.",
  "A longer time horizon means fewer competitors.",
  "It’s the choices you make, not the money you have."],
 "Black Arrow, delisted and valued at zero in the fund, declared a one-penny dividend: money from nothing.",
 ["arrow","cash-out","pence","fraud","school","margins"])

letter("2012-06", "Information as food", 23.3, 5.9,
 "David Attenborough once pointed out on the radio that Darwin travelled for four years and spent the rest of his life thinking. Sleep endorses that model, studying hard and then really thinking, over gathering ever more data. Great businesses often rest on simple human reactions that haven’t changed in millennia. A 1927 chart of Ford’s Model T, with prices falling as volumes soared, shows the same model Wal-Mart, Southwest and Amazon later used. Borrowing an analogy that treats information like food, the letter gives the most weight to facts with the longest shelf life. The management fee, which only covers costs, is heading below 0.1% a year. Against a standard 1% fee, that saves partners, mostly charities and endowments, about $15m a year. A reopening in January closed within two weeks.",
 ["Think more and collect less.",
  "Give the most weight to the most durable information.",
  "Lower fees might improve how the industry behaves.",
  "Information overload is really a failure of filtering."],
 "The ‘expensive tissue’ hypothesis: primates trade gut for brain, and a big brain means you needn’t spend all day grazing.",
 ["attenborough","rangaswami","food","information","ford","data"])

letter("2012-12", "Watching the pennies", 39.8, 15.8,
 "All is quiet: no trades, just reading and deliberate attempts to ‘kill’ their own companies on paper. The founders of Nomad’s companies run cultures fixated on low costs, the business version of cycling coach Dave Brailsford’s ‘aggregation of marginal gains’. Sleep draws lessons from outside the office. Carpetright’s founder saves on price tags while backing a federation of academy schools. Sleep is a governor at a school heading from an 85% exam failure rate toward an 85% pass rate on no extra money. And Zakaria’s family runs a children’s play centre. It paid staff more, spent on what parents valued and, on Zak’s advice, cut prices once it became profitable, to keep rivals away.",
 ["Doing nothing is still a decision.",
  "Know good costs from bad costs.",
  "Earn a little less for a lot longer.",
  "Practise in life what you preach in investing."],
 "A Glasgow property agent said rents used to be set to the penny, but now everything is a round number because nobody cares about pennies. Galactic HQ’s rent, Sleep confesses, is a round number.",
 ["pennies","centre","school","harris","round","children"])

letter("2013-06", "When six percent isn’t six percent", 20.8, 8.4,
 "The fee terms were sketched a decade earlier over a glass of wine in California: no profit from the management fee, a 6% hurdle for the cost of capital, and performance fees at risk for years. In practice, the maths of losses and gains means the hurdle is well above 6%. So does a fee reserve that is itself invested in Nomad. They are happy to leave it that way. Drawing on Dan Ariely’s experiments (dismantled Lego robots, cake mixes, origami), Sleep argues that meaning motivates people as much as money. That is why founders such as Bezos, Buffett and Asos’s Nick Robertson care little about their pay. Trading has almost stopped. Nomad’s companies were about 15 years old when bought, with long runways ahead.",
 ["Meaning matters as much as money.",
  "Incentives are necessary but not sufficient.",
  "Young companies have long runways.",
  "Inactivity can add value."],
 "A joke ‘Nomad Inactivity App’ would let partners follow the lack of trading in real time, available only from Amazon’s app store.",
 ["robots","sisypheans","origami","ariely","meaning","rewards"])

letter("2013-12", "The last letter", 62.2, 26.7,
 "The 25th letter, which turned out to be the last. A dollar is now $10.21 before fees, against $2.17 for the index, and after fees Nomad compounded at over 18% a year. Sleep insists that the companies created the wealth, through their relationships with their customers. The managers just caught some good waves, for about 0.1% a year in fees. He laments heavier regulation: four regulators, and rules that treat a simple long-term fund like a leveraged hedge fund. He suggests taxing short-term investing instead. The Zimbabwe adventure ends. After hyperinflation and a frozen market, the shares were sold for three to eight times their cost in dollars, and partners received a 100-trillion Zimbabwe dollar note as a souvenir. Barry Schwartz’s paradox of choice explains why investors always feel someone else did better.",
 ["Fund managers shuffle wealth; companies create it.",
  "Regulation raises barriers for small, simple firms.",
  "Some adventures are not worth repeating.",
  "Too much choice breeds regret."],
 "A Ferrari 250 GTO had just sold for $52m, about 20% a year for fifty years. That was enough, Sleep jokes, to make Nomad’s record look feeble.",
 ["regulation","schwartz","choice","regulatory","zimbabwean","harare"])

assert len(L) == 24
for i, l in enumerate(L):
    l["words"] = totals[i]

def hits(a, b, c):
    s = a + b + c; assert len(s) == 24, s; return s

C = [
 dict(id="c1", name="Fifty-cent dollars", hits=hits("12212112","00100121","00000000"),
  def_="Buy a business for about half of what it is really worth, then judge progress by the portfolio’s price-to-value ratio rather than its share price. The December 2003 letter spells out the arithmetic. Buy at 50 cents and let value compound about 10% a year, and a winner returns roughly 26% annually. Even if half the portfolio merely stands still, the whole earns around 13%."),
 dict(id="c2", name="Scale economics shared", hits=hits("00100022","00210222","12121101"),
  def_="As a company grows, it hands the savings from its size back to customers as lower prices. Customers respond by buying more, which brings more scale and more savings, so size becomes a moat rather than a drag. Named in the Costco analysis of December 2004, the idea came to describe Amazon, AirAsia, Carpetright and GEICO, and by 2009 more than half of Nomad."),
 dict(id="c3", name="Destination analysis", hits=hits("00000000","21112011","00010000"),
  def_="Judge a business by where its engine is likely to take it over many years, not by this year’s results. Judge a fund by where it ends up, not by how smooth the ride was. The idea grew out of the goal of turning $1 into $16 over twenty years and was named in 2007, after the lessons of Conseco and Stagecoach."),
 dict(id="c4", name="Patience and the equity yield curve", hits=hits("02111100","21200200","11010010"),
  def_="Business outcomes are easier to foresee over five years than over five months, so the long end of the ‘equity yield curve’ has less competition and higher rewards. Other owners of Nomad’s stocks held them for about 20 weeks (2006) or 51 days (2008). Nomad expected to hold for around five years."),
 dict(id="c5", name="Concentration", hits=hits("00000210","10021002","10010000"),
  def_="With few genuine insights available, owning more stocks dilutes attention and can raise risk rather than lower it. The letters cite the Kelly criterion (2004) and suggest building a portfolio down from 100% rather than up from 1% (2007). By the end, around ten companies made up nearly all of Nomad."),
 dict(id="c6", name="Fair fees and the principal–agent gap", hits=hits("00001001","22210120","10102021"),
  def_="Managers and clients want different things, and the letters try to close the gap. The management fee only covered costs and fell as the fund grew. The performance fee applied above a 6% hurdle, sat in a refundable reserve and was paid out over years. After the 2008 losses, that reserve was refunded to partners."),
 dict(id="c7", name="Psychology of misjudgement", hits=hits("01001012","21012100","01200001"),
  def_="The lasting edge, Sleep argues, is behavioural. The letters work through social proof, vivid evidence, poor probabilistic thinking, impatience, commitment bias, denial, anchoring and drift. The illustrations range from a Punch cartoon to a bridge champion to psychology experiments."),
 dict(id="c8", name="Learning from mistakes", hits=hits("01101110","10022202","10000000"),
  def_="Admit errors openly, measure them by the opportunities they cost, and learn enough that they end up paying for themselves. The biggest mistakes turned out to be selling great businesses too early: Stagecoach for Nomad, IBM and Wal-Mart for others."),
 dict(id="c9", name="Discounts to replacement cost", hits=hits("11100202","10000011","00000002"),
  def_="Buy hard assets far below what they would cost to rebuild, where nobody is adding supply and prices must eventually rise to justify new capacity. This drove Marathon’s cement wins after the Asian crisis and Nomad’s Philippine and Zimbabwean holdings."),
 dict(id="c10", name="Character and founders", hits=hits("10020200","00020101","21010110"),
  def_="Prefer companies that behave well because they want to, run by owner-minded people who allocate capital rationally over many years. The office kept a list of ‘super-high-quality thinkers’. By 2007–08, some 85–90% of Nomad was in founder- or owner-run firms."),
 dict(id="c11", name="Size, opening and closing", hits=hits("00012200","21010010","00001000"),
  def_="Take new money only when it can buy fresh bargains, close otherwise, and keep the right to shrink. Nomad closed at about $100m in 2004 and reopened in the 2008 crash. A 2012 reopening closed again within two weeks."),
 dict(id="c12", name="Rules versus thinking", hits=hits("00020002","00100100","00100002"),
  def_="Rulebooks, whether narrow mandates or box-ticking regulation, let people stop thinking. Nomad’s broad mandate (unlisted shares, preferred shares, any country) was an edge. The Carlisle roundabout and an insurance founder’s notice mocking rules became running jokes, and heavier regulation dominates the last letter."),
 dict(id="c13", name="Owning enough to act", hits=hits("00002200","10200100","00000000"),
  def_="Hold stakes big enough to be heard. In the UK, owning more than 10% lets you block a compulsory takeover. After losing Weetabix to a low bid, Nomad backed other shareholders’ campaigns. It later became the largest shareholder, or part of a blocking group, in several UK companies."),
 dict(id="c14", name="Slack, quiet and inactivity", hits=hits("00000000","00001022","10002220"),
  def_="Leave room in cash, time and attention to think, and resist the urge to say or do something. From 2008 the letters praise slack, quiet companies and the value of not trading. By 2013, buying and selling had almost stopped."),
 dict(id="c15", name="Growth versus value is a false split", hits=hits("00000020","00000001","00100000"),
  def_="A business is worth the cash it will produce, so growth is part of value, not a rival style. Shortcut ratios miss this, which is how a company like Wal-Mart stayed undervalued for decades."),
 dict(id="c16", name="Borrowing from other fields", hits=hits("00000000","10120000","01001010"),
  def_="Many problems go unsolved because they fall between disciplines. The letters borrow from the Santa Fe Institute (complexity and scaling laws), behavioural finance, biology, anthropology and psychology."),
]
for c in C:
    c["def"] = c.pop("def_")

MODELS = {
 "ses": dict(name="Scale economics shared", color="var(--route)"),
 "asset": dict(name="Discount to replacement cost", color="var(--contour)"),
 "turn": dict(name="Turnaround or workout", color="var(--grid)"),
 "fr": dict(name="Franchise or quality", color="var(--wood)"),
 "ref": dict(name="Cited, not a core holding", color="var(--ref)"),
}

H0 = [
 ("speedway","International Speedway","United States","fr","Owned in the early years","NASCAR track owner. Buying up circuits improved its bargaining power with TV networks. One of two holdings described in the first letter."),
 ("matichon","Matichon","Thailand","fr","Owned for years","Debt-free Thai newspaper bought for a fraction of its value. In 2005, Nomad refused to sell into a takeover attempt reportedly backed by the prime minister."),
 ("xerox","Xerox","United States","turn","Owned","Shunned after an accounting restatement that left cash flow untouched. Bought at under half of Nomad’s estimate of its worth."),
 ("monsanto","Monsanto","United States","fr","Owned briefly; sold at about cost","A good business at a low price, until Nomad found an indemnity for a former subsidiary’s pollution liabilities that it had missed. Sold at roughly cost, and the first mistake the letters confess."),
 ("estee","Estée Lauder","United States","ref","Admired, never cheap enough","Its shares fell when it chose to spend more on building its brands. The letters cite this as the market punishing a company for long-term sense."),
 ("conseco","Conseco","United States","turn","Owned; went bankrupt","Insurer that went bankrupt in December 2002. Later dissected as a lesson in anchoring on the original analysis."),
 ("stagecoach","Stagecoach","United Kingdom","turn","Owned; sold too early","UK bus operator bought at 14p as its founder returned to fix it. The biggest early winner, and later called the biggest mistake: sold near 90p, it went on to trade above £2.50."),
 ("costco","Costco","United States","ses","Core holding from 2002","Warehouse club with a fixed, low mark-up. Bought in 2002, dissected in 2004, and the template for ‘scale economics shared’."),
 ("kersaf","Kersaf","South Africa","asset","Owned","Casino and hotel group whose strategy changed after Allan Gray and Marathon voted their shares together."),
 ("weetabix","Weetabix","United Kingdom (unlisted)","fr","Owned until its 2004 buyout","Family-controlled cereal maker whose shares traded off-exchange. Bought near £20 against an estimated £70, then taken private by Hicks Muse at £53.75 over Nomad’s objection."),
 ("lucent","Lucent preferred shares","United States","turn","Owned; sold at full value","8% redeemable preferred shares bought far below par. They tripled once the company raised equity, and Nomad sold them."),
 ("erie","Erie Family Life","United States","ref","Researched","Turned up by a screen for companies whose share count hadn’t changed in a decade, a lesson in per-share discipline."),
 ("jardine","Jardine Matheson / Strategic","Hong Kong","asset","Owned","Asian conglomerate priced below the value of its assets, about 6.5% of the fund in 2004. Other shareholders pushed it to reorganise."),
 ("unioncement","Union Cement","Philippines","asset","Owned (a small stake)","Cement maker priced at a quarter of replacement cost, but so illiquid that Nomad built only a 1% position before Holcim bought control at five times Nomad’s average price."),
 ("telewest","Telewest","United Kingdom","turn","Owned through restructuring","UK cable operator bought through its restructuring (later Virgin Media). One of six holdings that received bids in 2004–05."),
 ("newworld","New World Development","Hong Kong","asset","Owned","Hong Kong developer, named in 2005 as an idea that could have absorbed far more money."),
 ("dell","Dell","United States","ses","Admired in 2004; owned by 2007","Praised in 2004 for passing its scale benefits on to buyers. By 2007 it was held as a company recovering from its mistakes."),
 ("ebay","eBay","United States","ref","Admired","Floated in 2004 as a candidate for the world’s most valuable business: a huge marketplace that tends toward a single winner and needs very little new capital to grow."),
 ("walmart","Wal-Mart","United States","ref","The recurring example","Thrift shared with customers, undervalued for decades, and very costly to sell early. The letters return to it again and again."),
 ("berkshire","Berkshire Hathaway","United States","ses","Owned","Held for businesses that share scale with customers, such as GEICO and Nebraska Furniture Mart. With Costco, one of the portfolio’s two ‘grandparents’."),
 ("zimbabwe","Zimbabwe basket","Zimbabwe","asset","A basket of small holdings; sold 2013","Cement, brewing and construction shares bought at tiny fractions of replacement cost. Written down to zero in 2008, then sold for three to eight times their cost in 2013."),
 ("siam","Siam Cement","Thailand","ref","Marathon-era example","The Asian-crisis template from before Nomad: huge cement assets priced below replacement cost, which went on to rise about twentyfold."),
 ("northwest","Northwest Airlines","United States","turn","Owned","The airline that taught a lesson: high insider ownership can slow down a necessary restructuring."),
 ("amazon","Amazon","United States","ses","Owned","A sixth of Nomad by mid-2007, and the defining holding of the later letters, which quote Jeff Bezos often."),
 ("liberty","Liberty Media / Global","Europe and Japan","turn","Owned","Named in 2007 among the companies recovering from their mistakes."),
 ("games","Games Workshop","United Kingdom","fr","Owned; largest shareholder","The Warhammer maker. Nomad was its largest shareholder by 2006. In 2008 its chairman admitted the firm had grown complacent, and the market valued it at little more than its equipment."),
 ("whiteheadmann","Whitehead Mann","United Kingdom","turn","Part of a dissenting group","UK headhunter taken private at a low price. Nomad joined a group of dissenting shareholders who together held enough shares not to be forced out."),
 ("mdc","MDC Holdings","United States","ref","Cited","A US homebuilder that learned from its early-1990s near miss. The letters contrast it with a bank that drew the wrong lesson from its own."),
 ("airasia","AirAsia","Malaysia","ses","Owned","Perhaps the world’s lowest-cost airline. In 2008 it was priced below the value of its own planes."),
 ("mbia","MBIA","United States","turn","Owned briefly; sold 2008","Bond insurer bought after its crisis began and sold within months. The risk of share issuance at low prices made its value per share unknowable."),
 ("carpetright","Carpetright","United Kingdom","ses","Owned","UK carpet retailer whose founder, Lord Harris, counted every penny, down to reusable price tags."),
 ("gm","General Motors","United States","ref","Cited","The loud counter-example, with the biggest advertising budget of any annual report they read."),
 ("michaelpage","Michael Page","United Kingdom","fr","Owned","Recruitment firm praised for sharing commissions fairly in an eat-what-you-kill industry."),
 ("asos","Asos","United Kingdom","ses","Owned","Online fashion retailer. Its founder told them he was having more fun than ever."),
 ("welsh","A Welsh motor insurer","United Kingdom","ref","Visited (unnamed)","An unnamed insurer whose edge came from doing many small things slightly better than its rivals."),
 ("blackarrow","Black Arrow","United Kingdom","turn","Owned; delisted","A delisted holding valued at zero in the fund, which then paid a one-penny dividend."),
]
Hrows = []
for key, name, where, model, status, note in H0:
    arr = ents[key]
    first = next((i for i, n in enumerate(arr) if n), 99)
    Hrows.append(dict(key=key, name=name, where=where, model=model, status=status, note=note, _f=first, _t=sum(arr)))
Hrows.sort(key=lambda r: (r["_f"], -r["_t"]))
for r in Hrows: r.pop("_f"); r.pop("_t")
ENTS = {r["key"]: ents[r["key"]] for r in Hrows}

# route: since-inception growth of $1 as printed in each letter
R = [
 (2001.69,"launch","10 Sept 2001",1.0,1.0,None,False),
 (2002.0,"2001-12","31 Dec 2001",1.101,1.039,0,False),
 (2002.5,"2002-06","30 Jun 2002",1.1454,0.9478,1,False),
 (2003.0,"2002-12","31 Dec 2002",1.1157,0.8372,2,False),
 (2003.5,"2003-06","30 Jun 2003",1.406,0.922,3,False),
 (2004.0,"2003-12","31 Dec 2003",2.004,1.105,4,False),
 (2004.5,"2004-06","30 Jun 2004",1.985,1.1437,5,False),
 (2005.0,"2004-12","31 Dec 2004",2.446,1.294,6,False),
 (2005.5,"2005-06","30 Jun 2005",2.505,1.289,7,False),
 (2006.0,"2005-12","31 Dec 2005",2.672,1.388,8,False),
 (2006.5,"2006-06","30 Jun 2006 (derived)",2.756,1.473,9,False),
 (2007.0,"2006-12","31 Dec 2006",3.032,1.702,10,False),
 (2007.5,"2007-06","30 Jun 2007",3.581,1.819,11,False),
 (2008.0,"2007-12","31 Dec 2007",3.690,1.816,12,False),
 (2008.5,"2008-06","30 Jun 2008",2.930,1.625,13,False),
 (2009.0,"2008-12","31 Dec 2008",2.011,1.077,14,False),
 (2009.5,"2009-06","30 Jun 2009",2.448,1.146,15,False),
 (2010.0,"2009-12","31 Dec 2009",3.450,1.400,16,False),
 (2010.5,"2010-06","30 Jun 2010",3.382,1.262,17,False),
 (2011.0,"2010-12","31 Dec 2010 (derived)",4.965,1.565,None,True),
 (2011.5,"2011-06","30 Jun 2011",5.875,1.647,18,False),
 (2012.0,"2011-12","31 Dec 2011",4.476,1.479,19,False),
 (2012.5,"2012-06","30 Jun 2012",5.552,1.565,20,False),
 (2013.0,"2012-12","31 Dec 2012",6.294,1.713,21,False),
 (2013.5,"2013-06","30 Jun 2013",7.602,1.856,22,False),
 (2014.0,"2013-12","31 Dec 2013",10.211,2.169,23,False),
]
route = [dict(t=t,key=k,date=d,nomad=n,idx=i,letter=l,derived=dv) for t,k,d,n,i,l,dv in R]

annual = [dict(y=y,n=n,i=i) for y,n,i in zip(range(2001,2014),
  [10.1,1.3,79.6,22.1,9.2,13.6,21.2,-45.3,71.5,43.9,-9.9,39.8,62.2],
  [3.6,-19.9,33.1,14.7,9.5,20.1,9.0,-40.7,30.0,11.8,-5.5,15.8,26.7])]

mix = [
 dict(title="December 2002: grouped by kind of bargain", parts=[
   dict(name="Hard-to-copy franchises",v=41,color="var(--wood)"),
   dict(name="Asset-backed discounts",v=31,color="var(--contour)"),
   dict(name="Deep-value workouts",v=22,color="var(--grid)"),
   dict(name="Cash and other",v=6,color="var(--ref)",approx=True)]),
 dict(title="June 2009: grouped by business model", parts=[
   dict(name="Scale economics shared",v=52,color="var(--route)",approx=True),
   dict(name="Discount to replacement cost",v=15,color="var(--contour)",approx=True),
   dict(name="‘Hated agencies’",v=15,color="var(--agency)"),
   dict(name="Super-high-quality thinkers",v=9,color="var(--wood)",approx=True),
   dict(name="Other",v=9,color="var(--ref)",approx=True)]),
]
pv = [
 dict(t=2002.5,v=51,label="June 2002"),
 dict(t=2003.0,v=50,label="December 2002"),
 dict(t=2003.5,v=65,label="June 2003"),
 dict(t=2004.0,v=65,label="December 2003"),
 dict(t=2004.5,v=61,label="June 2004"),
 dict(t=2005.0,v=73,label="December 2004"),
 dict(t=2005.5,v=68,label="June 2005"),
 dict(t=2007.0,v=68,approx=True,label="December 2006",note="In the upper 60s, up from the low 60s in October"),
 dict(t=2009.5,v=45,approx=True,lt=True,gap=True,label="June 2009",note="Meaningfully less than half of their appraisal"),
]
holdp = [
 dict(name="Nomad’s intended holding period",w=260,nomad=True),
 dict(name="Typical mutual fund manager (per Jack Bogle)",w=47.7),
 dict(name="Other owners of Nomad’s stocks (2006)",w=20),
 dict(name="Phelps Dodge shareholders (2006)",w=13),
 dict(name="Owners of Nomad’s US stocks (2008)",w=7.3),
]
fee = [
 dict(t=2001.7,v=10),
 dict(t=2004.2,v=10,mark=True,label="2001 – Sept 2006",note="0.1% a year, leaning on Marathon’s infrastructure",tag="Marathon era: 10"),
 dict(t=2006.7,v=10),
 dict(t=2006.78,v=50,mark=True,approx=True,label="Late 2006",note="About 50 bp when Sleep, Zakaria & Co. started out",tag="≈50",anchor="start",dx=8),
 dict(t=2007.5,v=32,mark=True,approx=True,label="June 2007",note="Settling in the low 30s",tag="low 30s",anchor="start",dx=8),
 dict(t=2009.5,v=20,mark=True,approx=True,label="June 2009",note="Around 20 bp",tag="≈20"),
 dict(t=2012.5,v=10,mark=True,approx=True,label="June 2012",note="Heading below 10 bp",tag="<10"),
 dict(t=2013.99,v=10,mark=True,approx=True,label="December 2013",note="Around 10 bp",tag="≈10",anchor="end",dx=-4),
]

def write_page():
    jr = json.load(open(DATA / "jev_results.json"))
    jev = dict(model=next(iter(jr["model"])), paragraphs=sum(c["n"] for c in next(iter(jr["grid"].values()))),
               grid={cid: [[c["share"], c["k"], c["n"]] for c in row] for cid, row in jr["grid"].items()})
    ex = json.load(open(DATA / "extras_results.json"))
    wp = json.load(open(DATA / "writer_paths_out.json")) if (DATA / "writer_paths_out.json").exists() else {"paths": {}, "voice": {}}
    wa = json.load(open(DATA / "writer_ask_out.json")) if (DATA / "writer_ask_out.json").exists() else {}
    for lst in ex["paths"].values():
        for e in lst: e["note"] = wp.get("paths", {}).get(e["ref"]); e.pop("i", None)
    for lst in ex["voice"]["tops"].values():
        for e in lst: e["note"] = wp.get("voice", {}).get(e["ref"]); e.pop("i", None)
    for a in ex["ask"]:
        w = wa.get(a["qid"], {}); a["answer"] = w.get("answer"); used = set(w.get("used") or [])
        for n, hit in enumerate(a["hits"]): hit["used"] = n in used
    page = dict(extras=ex, jev=jev, letters=L, concepts=C, models=MODELS, holdings=Hrows, ents=ENTS, route=route, annual=annual,
                mix=mix, pv=pv, holdp=holdp, fee=fee, totals=totals, words=words)
    blob = "const DATA=" + json.dumps(page, ensure_ascii=False, separators=(",", ":")) + ";"
    blob = blob.replace("</", "<\\/")
    tpl = open(SRC / "template.html", encoding="utf-8").read()
    frag = tpl.replace("/*__DATA__*/", blob)
    # The template is a fragment (head tags, then body content). Wrap it into a full document so any
    # static host serves it as UTF-8 in standards mode with a mobile viewport.
    cut = frag.index("</style>") + len("</style>")
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           + frag[:cut] + "\n</head>\n<body>\n" + frag[cut:].lstrip("\n") + "\n</body>\n</html>\n")
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(doc, encoding="utf-8")
    if "--fragment" in sys.argv:  # bare version for hosts that add their own <head> (e.g. claude.ai Artifacts)
        Path(sys.argv[sys.argv.index("--fragment") + 1]).write_text(frag, encoding="utf-8")
    print("written", len(doc)//1024, "KB; holdings rows", len(Hrows))
    # sanity: distinctive words exist in index
    idx = set(p.split(":",1)[0] for p in words.split("|"))
    for l in L:
        miss = [w for w in l["distinct"] if w not in idx]
        if miss: print("missing", l["id"], miss)

if __name__ == "__main__":
    write_page()
