# 41-problem expansion plan (working doc, not delivered)

## Mandatory (26)
### Hard-missing topics (7)
| slug | title | topic | difficulty | tier | LC ref |
|---|---|---|---|---|---|
| lru-cache | LRU Cache | hashing | Hard | advanced | LC146 |
| reverse-nodes-k-group | Reverse Nodes in k-Group | linked-lists | Hard | advanced | LC25 |
| shortest-subarray-sum-at-least-k | Shortest Subarray with Sum at Least K | queues | Hard | advanced | LC862 |
| count-smaller-after-self | Count of Smaller Numbers After Self | sorting | Hard | advanced | LC315 |
| largest-rectangle-histogram | Largest Rectangle in Histogram | stacks | Hard | advanced | LC84 |
| basic-calculator | Basic Calculator | strings | Hard | advanced | LC224 |
| smallest-range-k-lists | Smallest Range Covering Elements from K Lists | two-pointer | Hard | advanced | LC632 |

### Complex (15, one per existing topic)
| slug | title | topic | LC ref |
|---|---|---|---|
| trapping-rain-water-ii | Trapping Rain Water II | arrays | LC407 |
| split-array-largest-sum | Split Array Largest Sum | binary-search | LC410 |
| regular-expression-matching | Regular Expression Matching | dynamic-programming | LC10 |
| alien-dictionary | Alien Dictionary | graphs | LC269 |
| substring-concat-all-words | Substring with Concatenation of All Words | hashing | LC30 |
| ipo-maximize-capital | IPO | heaps | LC502 |
| lfu-cache | LFU Cache | linked-lists | LC460 |
| constrained-subsequence-sum | Constrained Subsequence Sum | queues | LC1425 |
| word-break-ii | Word Break II | recursion | LC140 |
| sliding-window-median | Sliding Window Median | sliding-window | LC480 |
| maximum-gap | Maximum Gap | sorting | LC164 |
| maximal-rectangle | Maximal Rectangle | stacks | LC85 |
| text-justification | Text Justification | strings | LC68 |
| binary-tree-cameras | Binary Tree Cameras | trees | LC968 |
| minimum-window-subsequence | Minimum Window Subsequence | two-pointer | LC727 |

### Greedy (new topic, 4)
| slug | title | difficulty | tier | LC ref |
|---|---|---|---|---|
| assign-cookies | Assign Cookies | Easy | extended | LC455 |
| jump-game-ii | Jump Game II | Medium | extended | LC45 |
| candy | Candy | Hard | advanced | LC135 |
| course-schedule-iii | Course Schedule III | Complex | advanced | LC630 |

## Discretionary (15, all Medium, extended tier)
| slug | title | topic | LC ref |
|---|---|---|---|
| longest-increasing-subsequence | Longest Increasing Subsequence | dynamic-programming | LC300 |
| non-overlapping-intervals | Non-overlapping Intervals | arrays | LC435 |
| gas-station | Gas Station | greedy | LC134 |
| partition-labels | Partition Labels | greedy | LC763 |
| word-search | Word Search | recursion | LC79 |
| rotate-image | Rotate Image | arrays | LC48 |
| spiral-matrix | Spiral Matrix | arrays | LC54 |
| kth-smallest-sorted-matrix | Kth Smallest Element in a Sorted Matrix | heaps | LC378 |
| course-schedule-ii | Course Schedule II | graphs | LC210 |
| next-permutation | Next Permutation | arrays | LC31 |
| decode-ways | Decode Ways | dynamic-programming | LC91 |
| remove-k-digits | Remove K Digits | stacks | LC402 |
| bst-iterator | Binary Search Tree Iterator | trees | LC173 |
| reorganize-string | Reorganize String | heaps | LC767 |
| meeting-rooms-ii | Meeting Rooms II | heaps | LC253 |

Total: 7 + 15 + 4 + 15 = 41. Final bank: 109 + 41 = 150.

## Other approved changes
- jump-game: extended -> core, day 8 (Array patterns I), Day 8 minutes 210->240.
- New pattern_families.py rule: greedy-flavored patterns -> "Greedy" family (does not change existing two-pointer-same-direction rule's priority for problems already claimed by it; only newly-authored greedy problems use pattern text that trips the new rule).
- Concept lesson `greedy` (topic='greedy', kind='pattern') -- links dynamically ONLY to topic='greedy' problems (architectural finding: concept-lesson auto-linking is exact-topic-match only, cross-topic linking isn't supported by the existing mechanism -- see report item 11). max-area-container/jump-game/boats-to-save-people/task-scheduler referenced by markdown link in lesson prose instead, topic column left untouched.
- Difficulty CSS token: --complex / --complex-soft, .difficulty-Complex.
- Curriculum: 45 -> 50 days. Day43 unchanged (Full revision, 240m). Day44 unchanged budget (240m), text rewritten to drop "Mock Interview Mode". Day45 budget unchanged (210m), role becomes "Mixed-problem interview practice", text rewritten. New Day46 Weak-area revision, Day47 Advanced/Complex practice, Day48 Mock interview 4, Day49 Full-length final simulation, Day50 Final review & wrap-up.
