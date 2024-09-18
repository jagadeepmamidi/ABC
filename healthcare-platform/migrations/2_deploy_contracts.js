const HealthcarePlatform = artifacts.require("HealthcarePlatform");

module.exports = function (deployer) {
    deployer.deploy(HealthcarePlatform, 1000000); // Initial supply of 1,000,000 tokens
};
    