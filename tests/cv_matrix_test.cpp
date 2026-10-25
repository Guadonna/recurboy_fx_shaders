#include "CvMatrix.h"
#include <cassert>
#include <iostream>

using Masks = std::array<float, 4>;
using Adc = std::array<int, 3>;

static int count(const Masks& masks) {
    int result = 0;
    for (float mask : masks)
        for (int bit = 0; bit < 4; ++bit) result += (int(mask) >> bit) & 1;
    return result;
}

static void emit(const Masks& masks) {
    for (float mask : masks) std::cout << int(mask) << ' ';
    std::cout << '\n';
}

int main() {
    const Masks black{};
    for (unsigned seed = 0; seed < 100; ++seed) {
        CvMatrix matrix(seed);
        assert(matrix.rows() == black);
        matrix.update({{10, 10, 10}});
        assert(matrix.rows() == black);
        for (int channel = 0; channel < 3; ++channel) {
            Masks previous{};
            int seen = 0;
            matrix.reset();
            for (int gate = 0; gate < 100; ++gate) {
                Adc adc{{0, 0, 0}};
                adc[channel] = 11;
                matrix.update(adc);
                const Masks selected = matrix.rows();
                assert(count(selected) == 4);
                if (gate > 0) {
                    assert(selected != previous);
                    if (channel == 2)
                        for (int row = 0; row < 4; ++row) assert(selected[row] != previous[row]);
                }
                for (int row = 0; row < 4; ++row) {
                    if (channel == 0) {
                        assert(selected[row] == 0 || selected[row] == 15);
                        if (selected[row] == 15) seen |= 1 << row;
                    } else {
                        const int mask = int(selected[row]);
                        assert(mask && !(mask & (mask - 1)));
                        if (channel == 1) assert(selected[row] == selected[0]);
                        seen |= mask;
                    }
                }
                // An envelope changing amplitude above threshold must not reshuffle.
                for (int level : {12, 400, 1023, 11}) {
                    adc[channel] = level;
                    matrix.update(adc);
                    assert(matrix.rows() == selected);
                }
                adc[channel] = 10;
                matrix.update(adc);
                assert(matrix.rows() == black);
                previous = selected;
            }
            assert(seen == 15);
        }
    }
    // Simultaneous gates combine by OR; falling gates remove only their contribution.
    CvMatrix combined(777), isolated(777);
    combined.update({{11, 0, 0}});
    const Masks row = combined.rows();
    combined.update({{11, 11, 0}});
    isolated.update({{11, 0, 0}});
    isolated.update({{0, 11, 0}});
    const Masks col = isolated.rows();
    for (int r = 0; r < 4; ++r)
        assert(int(combined.rows()[r]) == (int(row[r]) | int(col[r])));
    combined.update({{11, 11, 11}});
    isolated.update({{0, 0, 11}});
    const Masks scatter = isolated.rows();
    for (int r = 0; r < 4; ++r)
        assert(int(combined.rows()[r]) == (int(row[r]) | int(col[r]) | int(scatter[r])));
    combined.update({{0, 11, 11}});
    for (int r = 0; r < 4; ++r)
        assert(int(combined.rows()[r]) == (int(col[r]) | int(scatter[r])));
    combined.update({{0, 0, 11}});
    assert(combined.rows() == scatter);
    combined.update({{0, 0, 0}});
    assert(combined.rows() == black);
    combined.reset();
    assert(combined.rows() == black);
    combined.update({{11, 0, 0}});  // Already high at activation is the first gate.
    assert(count(combined.rows()) == 4);

    // Actual state-machine outputs become the GLES end-to-end test inputs.
    CvMatrix fixture(123);
    emit(fixture.rows());
    for (Adc adc : {Adc{{11, 0, 0}}, Adc{{1023, 0, 0}}, Adc{{10, 0, 0}},
                    Adc{{11, 0, 0}}, Adc{{0, 11, 0}}, Adc{{0, 0, 11}},
                    Adc{{11, 11, 11}}, Adc{{0, 0, 0}}}) {
        fixture.update(adc);
        emit(fixture.rows());
    }
}
