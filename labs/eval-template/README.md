# The twenty-row eval

Chapter 14. Two pages of the book, and the highest-leverage operational habit
in it.

---

## Why bother

You cannot tell whether a capability improved unless you have something to
measure against. Public benchmarks won't do it, for three reasons: they're
contaminated, they're gamed, and above all **they don't measure your task**.

What you need instead is small and unglamorous: twenty to fifty examples of
your actual task, with a scoring rule you'd defend, kept in a file.

That's it. An afternoon of work, and it's worth more than any leaderboard:

- **It measures the thing you care about.** Nothing else does.
- **It catches silent regressions.** Vendors update models behind stable names.
  This happens, and without a baseline it is completely invisible until a
  customer finds it.
- **It converts every model release from a marketing event into a
  fifteen-minute measurement.**

The team that has this makes better calls than the team that doesn't, by a wide
margin.

---

## How to build one

1. **Start with `eval_template.csv`.** Rows 1–6 are generic warm-ups. They are
   not the point.

2. **Rows 7–10 are the point.** Replace them with real examples from your
   product. Include at least:
   - the input that broke last time
   - the case your team argues about
   - something a real user actually sent that went wrong

3. **Write the ideal output.** Not a rubric, not a description — the actual
   text you'd want back. If you can't write it, you don't yet know what correct
   means, and that is itself the finding. Stop and resolve it before building
   anything.

4. **Score 0 / 0.5 / 1.** Resist finer scales. You will not be consistent at
   1–10 and neither will anyone else.

5. **Re-run on every change.** New model, new prompt, new vendor version, new
   quantization. Same file, new column.

---

## Rules that make it work

**Twenty rows beats zero rows.** Do not wait until you have a hundred. The
value is in having a baseline at all.

**Score before you look at the diff.** Otherwise you'll rationalise.

**Keep it in version control** next to the code, not in someone's Drive.

**Add a row every time something goes wrong in production.** After a year this
file is the most valuable artifact your team owns about the feature, and it
cost nothing to build.

**Differences under about 5% on a small set are noise**, not improvement.

---

## The uncomfortable part

The first time you use this properly, you will change one word in a prompt,
feel certain it's better, run the eval, and find it's worse.

That moment is the whole point. Everything before it was vibes.
