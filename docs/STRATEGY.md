# PEAD Strategy

## 1. Overview

This project investigates a trading strategy based on **Post-Earnings Announcement Drift (PEAD)**.

This strategy is not quite a hypothesis – PEAD is an extremely well documented market phenomena that still has edge to this day. I personally love the prospect of being able to generate a strategy from home – the only barrier to entry being a programming project like this. 
I also look to explore different implementations of this strategy through testing different indicators, position sizing methods, e.t.c. Modern literature on this topic claims that the edge is disappearing, but I hope to test this directly. 

Most importantly, because I know I am not a financial expert, I have two super simple goals for this project while trying to learn:  
**Don't overfit and keep the strategy simple**

Note: most technical jargon in this document is from people much smarter than me in this space, I understand them conceptually and how to implement them in code.

My explanation of the strategy is derived from what I've read: when I say the strategy "IS" or "THIS IS" (i.e, when I speak matter-of-fact), I am really saying "studies show...and studies claim..." Speaking matter-of-fact just makes it easier to read. 


---

# 2. Strategy Background

The strategy is based on two super simple observations:

1. **Earnings surprises contain information about future returns.**
2. **The market may not represent this information immediately but will eventually DRIFT in the direction of EPS surprise.**

> Ex: EPS surprise of 12% causes only a daily gain of 6% on the same day earnings were released. Over the course of 2 months, the stock may drift towards a net return from the day of earnings to 20%. 

Let the earnings surprise be $S_i$, where $S_i$ is simply the percent error between what financial analysts expected the earnings to be, and what the actual earnings were.

A positive $S_i$ represents a positive earnings surprise, while a negative $S_i$ represents a negative surprise.

It is well documented that the greater $S_i$ the greater the size of the market drift. 

---

# 3. Entry Parameters

## 3.1 Earnings Surprise

A stock first qualifies for consideration when its earnings surprise is sufficiently large.

The baseline strategy distinguishes between:

$$
S_i > 0
$$

and

$$
S_i < 0
$$

Positive surprises create  **long** positions and negative surprises create potential **short** positions.

As of right now there is no minimum threshold. Meaning if we have $S_i = 0.0000001$ for example, this will be considered for a trade. As I said, this is a Beta version, meaning many features are missing.  

The strategy will eventually include a minimum threshold of: $|S_i| \geq S_{min}$

where $S_{min}$ represents the minimum earnings surprise required to generate a signal.

---

## 3.2 Post-Earnings Price Confirmation

This strategy does not immediately enter a position solely because an earnings surprise occurred.

Instead, we use a stock's subsequent price movement as used as additional confirmation.

Take $R_{\text{day}+1}$, where $R_{\text{day}+1}$ is the daily return of a stock one day after the earnings call. 

For a positive earnings surprise:

$$
R_{\text{day}+1} > 0
$$

generates a long signal.

For a negative earnings surprise:

$$
R_{\text{day}+1} < 0
$$

generates a short signal.

This produces the basic decision rule:

$$ 
\text{Direction}_i = 
\begin{cases} 
\text{Long},  & \text{if } S_i > 0 \land R_{i, \text{day}+1} > 0 \\ 
\text{Short}, & \text{if } S_i < 0 \land R_{i, \text{day}+1} < 0 \\ 
\text{No Trade}, & \text{otherwise} 
\end{cases} 
$$

I will likely remove this confirmation step, since we can actually miss very good opportunities when the market adjusts the day after to a better, cheaper price for the stock (market tends to still drift). 

---

# 4. Holding Period

The baseline strategy uses a fixed holding period of about 60 days. Simply:

$$
\text{exit date} = \text{entry date} + H
$$

where $H$ is the holding period of 60 days. Likely the exit will change naturally based off revisions to things such as the stop loss, which will likely be trailing and could curtail our trade.  

---

# 5. Baseline Position Sizing

For Beta, we use a static percent of available cash for position sizing.

Let:  

$$E_t = \text{portfolio equity at entry}$$
$$w = \text{target position allocation}$$

Then:

$$
PositionSize_i = E_t \times w
$$

The current baseline uses:

$$
w = 0.02
$$

or 2% of available portfolio equity per position, subject to available cash.


---

# 6. Proposed Rank-Based Position Sizing

As of now we treat each signal as equally good and equally bad. We are drastically selling this strategy short by doing so, especially when we have previously established that larger EPS surprise means larger potential drift.

Each signal should therefore receive a score or rank. Many papers use deciles for a similar effect.  

Conceptually:  

$$
RankScore_i = f(S_i, V_i, \ldots)
$$

where:
$V_i = \text{volatility characteristics}$

The reason I leave the parameters of the function open is because in theory I would like to find other indicators that can make the rank score more accurate or stronger, but I don't trust myself to do this without having look-back bias or other shortcomings. I was never good at math. In fact, I hate it. 

---

# 7. Earnings-Surprise Component

Because earnings surprise magnitude is expected to be strongly related to PEAD strength, it should play a major role in the ranking system.

One possible normalized surprise score is:

$$
S_i^* =
\frac{|S_i| - S_{min}}
{S_{max} - S_{min}}
$$

where $S_i^*$ represents the normalized magnitude of the earnings surprise.

The sign of the original surprise determines trade direction, while its magnitude contributes to trade quality.

Thus:

$$
Direction_i = sign(S_i)
$$

while:

$$
Quality_i \propto |S_i|
$$

The important distinction is that **direction and conviction are separate concepts**.

---

# 8. Volatility-Adjusted Position Sizing

A large earnings surprise does not automatically justify a large position.

A highly volatile stock can produce substantially more portfolio risk than a similarly sized position in a stable stock.

Therefore, future position sizing should incorporate volatility.

Let:

- $\sigma_i$ = estimated volatility of stock $i$
- $Q_i$ = trade quality score

A simple conceptual sizing function is:

$$
W_i \propto \frac{Q_i}{\sigma_i}
$$

This gives greater allocation to high-quality opportunities while reducing exposure to unusually volatile stocks.

The resulting weights would then be normalized across all eligible trades.

For example:

$$
W_i =
\frac{\frac{Q_i}{\sigma_i}}
{\sum_{j=1}^{N}\frac{Q_j}{\sigma_j}}
$$

where $N$ is the number of simultaneous eligible trades.

This is only a starting framework. The relationship between volatility and PEAD returns must be empirically tested before being adopted as part of the production strategy.

---

# 9. Risk Constraints

The sizing system should not be allowed to allocate unlimited capital to a single highly ranked trade.

Future implementations should therefore impose constraints such as:

### Maximum position size

$$
W_i \leq W_{max}
$$

### Minimum position size

$$
W_i \geq W_{min}
$$

when a trade qualifies for execution.

### Maximum portfolio exposure

$$
\sum_{i=1}^{N} W_i \leq W_{portfolio,max}
$$

These constraints prevent the ranking system from concentrating the portfolio excessively in a small number of trades.

---

# 10. Proposed Composite Ranking Model

The eventual ranking system may combine multiple independent characteristics.

A general form is:

$$
Q_i = \alpha S_i^* + \beta C_i + \gamma M_i - \delta V_i^*
$$

where:

- $S_i^*$ = normalized earnings surprise
- $C_i$ = strength of post-earnings price confirmation
- $M_i$ = additional market or momentum characteristics
- $V_i^*$ = normalized volatility
- $\alpha,\beta,\gamma,\delta$ = empirically determined weights

This model should **not** initially be treated as an assumption that the coefficients are correct.

The coefficients and factors should instead be treated as hypotheses to be tested through backtesting.

---

# 11. Trade Ranking

At each point in time, eligible signals can be ranked:

$$
Q_{(1)} \geq Q_{(2)} \geq \cdots \geq Q_{(N)}
$$

where $Q_{(1)}$ represents the highest-ranked trade.

The portfolio can then allocate capital according to rank and risk rather than simply assigning every trade the same allocation.

A possible implementation is to divide trades into ranking tiers:

| Rank | Conviction | Target Allocation |
|---|---|---|
| Top | Very High | Largest |
| High | High | Large |
| Medium | Moderate | Moderate |
| Low | Low | Small / excluded |

The exact allocation boundaries will be determined through testing.

---

# 12. Stop Losses and Dynamic Exits

The baseline strategy currently uses a fixed holding period and does not employ a stop-loss mechanism.

Future versions will investigate whether dynamic exits improve risk-adjusted performance.

Potential mechanisms include:

- Fixed percentage stop
- ATR-based stop
- Volatility-based stop
- Trailing stop
- Maximum-loss constraint
- Signal-reversal exit

A generic volatility-based stop could be represented as:

$$
StopDistance_i = k\sigma_i
$$

where $k$ controls the allowed movement before the position is exited.

These mechanisms will be evaluated separately rather than introduced simultaneously, allowing their individual effects to be measured.

---

# 13. Baseline vs. Future Strategy

The project intentionally separates the **baseline strategy** from future enhancements.

### Baseline

- Earnings surprise
- Post-earnings price confirmation
- Long/short direction
- Fixed holding period
- Constant position allocation
- No stop loss

### Planned enhancements

- Earnings-surprise ranking
- Volatility-adjusted sizing
- Cross-sectional trade ranking
- Dynamic position allocation
- Trailing stops
- Volatility-based stops
- Portfolio exposure limits
- Improved trade selection

This separation is important because each enhancement should be tested against the baseline independently.

---

# 14. Research Objective

The ultimate objective is not simply to maximize raw backtested return.

The strategy should be evaluated across several dimensions:

$$
Performance =
f(Return,\ Risk,\ Drawdown,\ Consistency,\ Capacity)
$$

A successful modification should ideally improve returns without introducing disproportionate increases in:

- volatility
- maximum drawdown
- concentration
- turnover
- downside risk

The central research question is therefore:

> **Can information contained in earnings surprises be converted into a systematic trading strategy whose risk-adjusted returns remain attractive after realistic portfolio construction and risk management?**

The baseline implementation establishes the foundation for testing this question.
