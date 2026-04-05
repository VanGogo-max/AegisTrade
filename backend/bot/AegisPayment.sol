// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract AegisPayment {
    address public owner;
    address public treasury;
    IERC20 public usdt;

    uint256 public constant PLAN_BASIC  = 50  * 1e6;
    uint256 public constant PLAN_PRO    = 100 * 1e6;
    uint256 public constant PLAN_ELITE  = 200 * 1e6;
    uint256 public constant REFERRAL_PCT = 20;
    uint256 public constant SUB_DURATION = 30 days;

    struct Subscription {
        uint8   plan;
        uint256 expiresAt;
        address referredBy;
    }

    mapping(address => Subscription) public subscriptions;
    mapping(address => uint256) public referralEarnings;
    mapping(address => uint256) public referralCount;

    event Subscribed(address indexed user, uint8 plan, uint256 expiresAt, address referrer);
    event Renewed(address indexed user, uint8 plan, uint256 newExpiry);
    event ReferralPaid(address indexed referrer, address indexed user, uint256 amount);
    event Withdrawn(address indexed to, uint256 amount);

    modifier onlyOwner() { require(msg.sender == owner, "Not owner"); _; }

    constructor(address _usdt, address _treasury) {
        owner    = msg.sender;
        treasury = _treasury;
        usdt     = IERC20(_usdt);
    }

    function subscribe(uint8 plan, address referrer) external {
        require(plan >= 1 && plan <= 3, "Invalid plan");
        require(referrer != msg.sender, "Cannot refer yourself");

        uint256 price = _planPrice(plan);
        require(usdt.transferFrom(msg.sender, address(this), price), "USDT transfer failed");

        uint256 referralAmount = 0;
        address actualReferrer = address(0);

        if (referrer != address(0) && subscriptions[referrer].expiresAt > block.timestamp) {
            referralAmount = (price * REFERRAL_PCT) / 100;
            referralEarnings[referrer] += referralAmount;
            referralCount[referrer]    += 1;
            actualReferrer              = referrer;
            emit ReferralPaid(referrer, msg.sender, referralAmount);
        }

        require(usdt.transfer(treasury, price - referralAmount), "Treasury transfer failed");

        uint256 start = block.timestamp;
        if (subscriptions[msg.sender].expiresAt > start) {
            start = subscriptions[msg.sender].expiresAt;
        }

        subscriptions[msg.sender] = Subscription({
            plan:      plan,
            expiresAt: start + SUB_DURATION,
            referredBy: subscriptions[msg.sender].referredBy == address(0)
                            ? actualReferrer
                            : subscriptions[msg.sender].referredBy
        });

        if (start == block.timestamp) {
            emit Subscribed(msg.sender, plan, subscriptions[msg.sender].expiresAt, actualReferrer);
        } else {
            emit Renewed(msg.sender, plan, subscriptions[msg.sender].expiresAt);
        }
    }

    function withdrawReferral() external {
        uint256 amount = referralEarnings[msg.sender];
        require(amount > 0, "Nothing to withdraw");
        referralEarnings[msg.sender] = 0;
        require(usdt.transfer(msg.sender, amount), "Withdraw failed");
        emit Withdrawn(msg.sender, amount);
    }

    function isActive(address user) external view returns (bool) {
        return subscriptions[user].expiresAt > block.timestamp;
    }

    function userPlan(address user) external view returns (uint8) {
        if (subscriptions[user].expiresAt <= block.timestamp) return 0;
        return subscriptions[user].plan;
    }

    function daysRemaining(address user) external view returns (uint256) {
        if (subscriptions[user].expiresAt <= block.timestamp) return 0;
        return (subscriptions[user].expiresAt - block.timestamp) / 1 days;
    }

    function setTreasury(address _treasury) external onlyOwner {
        treasury = _treasury;
    }

    function transferOwnership(address newOwner) external onlyOwner {
        owner = newOwner;
    }

    function emergencyWithdraw() external onlyOwner {
        uint256 bal = usdt.balanceOf(address(this));
        usdt.transfer(owner, bal);
    }

    function _planPrice(uint8 plan) internal pure returns (uint256) {
        if (plan == 1) return PLAN_BASIC;
        if (plan == 2) return PLAN_PRO;
        return PLAN_ELITE;
    }
}
