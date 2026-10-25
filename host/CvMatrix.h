#pragma once

#include <array>
#include <cstdint>

// Pure CPU state, independent of openFrameworks; tested with real ADC counts.
class CvMatrix {
public:
    // MCP3008, nominal 5 V reference: 10 = 48.88 mV, 11 = 53.76 mV.
    // First representable sample at/above the requested 50 mV threshold.
    static const int thresholdAdc = 11;

    explicit CvMatrix(std::uint32_t seed = 0x6d2b79f5u) : rng_(seed ? seed : 1u) {
        reset();
    }

    void seed(std::uint32_t value) { rng_ = value ? value : 1u; }

    void reset() {
        high_.fill(false);
        row_ = column_ = -1;
        scattered_.fill(-1);
    }

    void update(const std::array<int, 3>& adc) {
        for (int input = 0; input < 3; ++input) {
            const bool high = adc[input] >= thresholdAdc;
            if (high && !high_[input]) {
                if (input == 0) row_ = pickDifferent(row_);
                if (input == 1) column_ = pickDifferent(column_);
                if (input == 2) {
                    for (int& column : scattered_) column = pickDifferent(column);
                }
            }
            high_[input] = high;
        }
    }

    std::array<float, 4> rows() const {
        std::array<float, 4> masks{};
        for (int row = 0; row < 4; ++row) {
            unsigned mask = high_[0] && row == row_ ? 15u : 0u;
            if (high_[1]) mask |= 1u << column_;
            if (high_[2]) mask |= 1u << scattered_[row];
            masks[row] = static_cast<float>(mask);
        }
        return masks;
    }

private:
    std::uint32_t next() {
        rng_ ^= rng_ << 13;
        rng_ ^= rng_ >> 17;
        rng_ ^= rng_ << 5;
        return rng_;
    }

    int pickDifferent(int previous) {
        return previous < 0 ? static_cast<int>(next() % 4u)
                            : (previous + 1 + static_cast<int>(next() % 3u)) % 4;
    }

    std::uint32_t rng_;
    std::array<bool, 3> high_;
    int row_, column_;
    std::array<int, 4> scattered_;
};
