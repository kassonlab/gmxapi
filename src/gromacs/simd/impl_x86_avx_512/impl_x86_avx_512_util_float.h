/*
 * This file is part of the GROMACS molecular simulation package.
 *
 * Copyright (c) 2014,2015,2016, by the GROMACS development team, led by
 * Mark Abraham, David van der Spoel, Berk Hess, and Erik Lindahl,
 * and including many others, as listed in the AUTHORS file in the
 * top-level source directory and at http://www.gromacs.org.
 *
 * GROMACS is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation; either version 2.1
 * of the License, or (at your option) any later version.
 *
 * GROMACS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with GROMACS; if not, see
 * http://www.gnu.org/licenses, or write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA.
 *
 * If you want to redistribute modifications to GROMACS, please
 * consider that scientific software is very special. Version
 * control is crucial - bugs must be traceable. We will be happy to
 * consider code for inclusion in the official distribution, but
 * derived work must not be called official GROMACS. Details are found
 * in the README & COPYING files - if they are missing, get the
 * official version at http://www.gromacs.org.
 *
 * To help us fund GROMACS development, we humbly ask that you cite
 * the research papers on the package. Check out http://www.gromacs.org.
 */

#ifndef GMX_SIMD_IMPL_X86_AVX_512_UTIL_FLOAT_H
#define GMX_SIMD_IMPL_X86_AVX_512_UTIL_FLOAT_H

#include "config.h"

#include <cassert>
#include <cstdint>

#include <immintrin.h>

#include "gromacs/utility/basedefinitions.h"

#include "impl_x86_avx_512_general.h"
#include "impl_x86_avx_512_simd_float.h"

namespace gmx
{

// On MIC it is better to use scatter operations, so we define the load routines
// that use a SIMD offset variable first.

template <int align>
static inline void gmx_simdcall
gatherLoadBySimdIntTranspose(const float *  base,
                             SimdFInt32     simdoffset,
                             SimdFloat *    v0,
                             SimdFloat *    v1,
                             SimdFloat *    v2,
                             SimdFloat *    v3)
{
    assert(std::size_t(base) % 16 == 0);
    assert(align % 4 == 0);

    // All instructions might be latency ~4 on MIC, so we use shifts where we
    // only need a single instruction (since the shift parameter is an immediate),
    // but multiplication otherwise.
    if (align == 4)
    {
        simdoffset = simdoffset << 2;
    }
    else if (align == 8)
    {
        simdoffset = simdoffset << 3;
    }
    else
    {
        simdoffset = simdoffset * SimdFInt32(align);
    }

    // The 4 corresponds to sizeof(float), but it must be an immediate, and with debug builds
    // gcc will not evaluate the sizeof() function at compile time.
    v0->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base,   4);
    v1->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base+1, 4);
    v2->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base+2, 4);
    v3->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base+3, 4);
}

template <int align>
static inline void gmx_simdcall
gatherLoadUBySimdIntTranspose(const float *  base,
                              SimdFInt32     simdoffset,
                              SimdFloat *    v0,
                              SimdFloat *    v1)
{
    // All instructions might be latency ~4 on MIC, so we use shifts where we
    // only need a single instruction (since the shift parameter is an immediate),
    // but multiplication otherwise.
    // For align == 2 we can merge the constant into the scale parameter,
    // which can take constants up to 8 in total.
    if (align == 2)
    {
        v0->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base,   align * 4);
        v1->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base+1, align * 4);
    }
    else
    {
        if (align == 4)
        {
            simdoffset = simdoffset << 2;
        }
        else if (align == 8)
        {
            simdoffset = simdoffset << 3;
        }
        else
        {
            simdoffset = simdoffset * SimdFInt32(align);
        }
        v0->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base,   4);
        v1->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base+1, 4);
    }
}

template <int align>
static inline void gmx_simdcall
gatherLoadBySimdIntTranspose(const float *   base,
                             SimdFInt32      simdoffset,
                             SimdFloat *     v0,
                             SimdFloat *     v1)
{
    assert(std::size_t(base) % 8 == 0);
    assert(align % 2 == 0);
    gatherLoadUBySimdIntTranspose<align>(base, simdoffset.simdInternal_, v0, v1);
}

template <int align>
static inline void gmx_simdcall
gatherLoadTranspose(const float *        base,
                    const std::int32_t   offset[],
                    SimdFloat *          v0,
                    SimdFloat *          v1,
                    SimdFloat *          v2,
                    SimdFloat *          v3)
{
    gatherLoadBySimdIntTranspose<align>(base, simdLoadFI(offset), v0, v1, v2, v3);
}

template <int align>
static inline void gmx_simdcall
gatherLoadTranspose(const float *        base,
                    const std::int32_t   offset[],
                    SimdFloat *          v0,
                    SimdFloat *          v1)
{
    gatherLoadBySimdIntTranspose<align>(base, simdLoadFI(offset), v0, v1);
}

static const int c_simdBestPairAlignmentFloat = 2;

template <int align>
static inline void gmx_simdcall
gatherLoadUTranspose(const float *        base,
                     const std::int32_t   offset[],
                     SimdFloat *          v0,
                     SimdFloat *          v1,
                     SimdFloat *          v2)
{
    SimdFInt32 simdoffset;

    assert(std::size_t(offset) % 64 == 0);

    simdoffset = simdLoadFI(offset);

    // All instructions might be latency ~4 on MIC, so we use shifts where we
    // only need a single instruction (since the shift parameter is an immediate),
    // but multiplication otherwise.
    if (align == 4)
    {
        simdoffset = simdoffset << 2;
    }
    else if (align == 8)
    {
        simdoffset = simdoffset << 3;
    }
    else
    {
        simdoffset = simdoffset * SimdFInt32(align);
    }

    v0->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base,   4);
    v1->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base+1, 4);
    v2->simdInternal_ = _mm512_i32gather_ps(simdoffset.simdInternal_, base+2, 4);
}


template <int align>
static inline void gmx_simdcall
transposeScatterStoreU(float *              base,
                       const std::int32_t   offset[],
                       SimdFloat            v0,
                       SimdFloat            v1,
                       SimdFloat            v2)
{
    SimdFInt32 simdoffset;

    assert(std::size_t(offset) % 64 == 0);

    simdoffset = simdLoadFI(offset);

    // All instructions might be latency ~4 on MIC, so we use shifts where we
    // only need a single instruction (since the shift parameter is an immediate),
    // but multiplication otherwise.
    if (align == 4)
    {
        simdoffset = simdoffset << 2;
    }
    else if (align == 8)
    {
        simdoffset = simdoffset << 3;
    }
    else
    {
        simdoffset = simdoffset * SimdFInt32(align);
    }

    _mm512_i32scatter_ps(base,   simdoffset.simdInternal_, v0.simdInternal_, 4);
    _mm512_i32scatter_ps(base+1, simdoffset.simdInternal_, v1.simdInternal_, 4);
    _mm512_i32scatter_ps(base+2, simdoffset.simdInternal_, v2.simdInternal_, 4);
}


template <int align>
static inline void gmx_simdcall
transposeScatterIncrU(float *              base,
                      const std::int32_t   offset[],
                      SimdFloat            v0,
                      SimdFloat            v1,
                      SimdFloat            v2)
{
    GMX_ALIGNED(float, GMX_SIMD_FLOAT_WIDTH)  rdata0[GMX_SIMD_FLOAT_WIDTH];
    GMX_ALIGNED(float, GMX_SIMD_FLOAT_WIDTH)  rdata1[GMX_SIMD_FLOAT_WIDTH];
    GMX_ALIGNED(float, GMX_SIMD_FLOAT_WIDTH)  rdata2[GMX_SIMD_FLOAT_WIDTH];

    store(rdata0, v0);
    store(rdata1, v1);
    store(rdata2, v2);

    for (int i = 0; i < GMX_SIMD_FLOAT_WIDTH; i++)
    {
        base[ align * offset[i] + 0] += rdata0[i];
        base[ align * offset[i] + 1] += rdata1[i];
        base[ align * offset[i] + 2] += rdata2[i];
    }
}

template <int align>
static inline void gmx_simdcall
transposeScatterDecrU(float *              base,
                      const std::int32_t   offset[],
                      SimdFloat            v0,
                      SimdFloat            v1,
                      SimdFloat            v2)
{
    GMX_ALIGNED(float, GMX_SIMD_FLOAT_WIDTH)  rdata0[GMX_SIMD_FLOAT_WIDTH];
    GMX_ALIGNED(float, GMX_SIMD_FLOAT_WIDTH)  rdata1[GMX_SIMD_FLOAT_WIDTH];
    GMX_ALIGNED(float, GMX_SIMD_FLOAT_WIDTH)  rdata2[GMX_SIMD_FLOAT_WIDTH];

    store(rdata0, v0);
    store(rdata1, v1);
    store(rdata2, v2);

    for (int i = 0; i < GMX_SIMD_FLOAT_WIDTH; i++)
    {
        base[ align * offset[i] + 0] -= rdata0[i];
        base[ align * offset[i] + 1] -= rdata1[i];
        base[ align * offset[i] + 2] -= rdata2[i];
    }
}

static inline void gmx_simdcall
expandScalarsToTriplets(SimdFloat    scalar,
                        SimdFloat *  triplets0,
                        SimdFloat *  triplets1,
                        SimdFloat *  triplets2)
{
    triplets0->simdInternal_ = _mm512_castsi512_ps(_mm512_permutexvar_epi32(_mm512_set_epi32(5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 0, 0, 0),
                                                                            _mm512_castps_si512(scalar.simdInternal_)));
    triplets1->simdInternal_ = _mm512_castsi512_ps(_mm512_permutexvar_epi32(_mm512_set_epi32(10, 10, 9, 9, 9, 8, 8, 8, 7, 7, 7, 6, 6, 6, 5, 5),
                                                                            _mm512_castps_si512(scalar.simdInternal_)));
    triplets2->simdInternal_ = _mm512_castsi512_ps(_mm512_permutexvar_epi32(_mm512_set_epi32(15, 15, 15, 14, 14, 14, 13, 13, 13, 12, 12, 12, 11, 11, 11, 10),
                                                                            _mm512_castps_si512(scalar.simdInternal_)));
}


static inline float gmx_simdcall
reduceIncr4ReturnSum(float *    m,
                     SimdFloat  v0,
                     SimdFloat  v1,
                     SimdFloat  v2,
                     SimdFloat  v3)
{
    __m512 t0, t1, t2;

    assert(std::size_t(m) % 16 == 0);

    t0 = _mm512_add_ps(v0.simdInternal_, _mm512_permute_ps(v0.simdInternal_, 0x4E));
    t0 = _mm512_mask_add_ps(t0, avx512Int2Mask(0xCCCC), v2.simdInternal_, _mm512_permute_ps(v2.simdInternal_, 0x4E));
    t1 = _mm512_add_ps(v1.simdInternal_, _mm512_permute_ps(v1.simdInternal_, 0x4E));
    t1 = _mm512_mask_add_ps(t1, avx512Int2Mask(0xCCCC), v3.simdInternal_, _mm512_permute_ps(v3.simdInternal_, 0x4E));
    t2 = _mm512_add_ps(t0, _mm512_permute_ps(t0, 0xB1));
    t2 = _mm512_mask_add_ps(t2, avx512Int2Mask(0xAAAA), t1, _mm512_permute_ps(t1, 0xB1));

    t2 = _mm512_add_ps(t2, _mm512_shuffle_f32x4(t2, t2, 0x4E));
    t2 = _mm512_add_ps(t2, _mm512_shuffle_f32x4(t2, t2, 0xB1));

    t0 = _mm512_maskz_loadu_ps(avx512Int2Mask(0xF), m);
    t0 = _mm512_add_ps(t0, t2);
    _mm512_mask_storeu_ps(m, avx512Int2Mask(0xF), t0);

    t2 = _mm512_add_ps(t2, _mm512_permute_ps(t2, 0x4E));
    t2 = _mm512_add_ps(t2, _mm512_permute_ps(t2, 0xB1));

    return *reinterpret_cast<float *>(&t2);

}

static inline SimdFloat gmx_simdcall
loadDualHsimd(const float * m0,
              const float * m1)
{
    assert(std::size_t(m0) % 32 == 0);
    assert(std::size_t(m1) % 32 == 0);

    return {
               _mm512_mask_loadu_ps(_mm512_maskz_loadu_ps(avx512Int2Mask(0x00FF), m0), avx512Int2Mask(0xFF00), m1-8)
    };
}

static inline SimdFloat gmx_simdcall
loadDuplicateHsimd(const float * m)
{
    assert(std::size_t(m) % 32 == 0);

    __m512 tmp;

    tmp = _mm512_maskz_loadu_ps(avx512Int2Mask(0x00FF), m);
    return {
               _mm512_shuffle_f32x4(tmp, tmp, 0x44)
    };
}

static inline SimdFloat gmx_simdcall
load1DualHsimd(const float * m)
{
    __m512 tmp;
    tmp = _mm512_maskz_expandloadu_ps(avx512Int2Mask(0x0101), m);
    tmp = _mm512_permute_ps(tmp, 0x00);
    return _mm512_shuffle_f32x4(tmp, tmp, 0xA0);
}


static inline void gmx_simdcall
storeDualHsimd(float *     m0,
               float *     m1,
               SimdFloat   a)
{
    assert(std::size_t(m0) % 32 == 0);
    assert(std::size_t(m1) % 32 == 0);

    _mm512_mask_storeu_ps(m0,   avx512Int2Mask(0x00FF), a.simdInternal_);
    _mm512_mask_storeu_ps(m1-8, avx512Int2Mask(0xFF00), a.simdInternal_);
}

static inline void gmx_simdcall
incrDualHsimd(float *     m0,
              float *     m1,
              SimdFloat   a)
{
    assert(std::size_t(m0) % 32 == 0);
    assert(std::size_t(m1) % 32 == 0);

    __m512 x;

    // Lower half
    x = _mm512_maskz_loadu_ps(avx512Int2Mask(0x00FF), m0);
    x = _mm512_add_ps(x, a.simdInternal_);
    _mm512_mask_storeu_ps(m0, avx512Int2Mask(0x00FF), x);

    // Upper half
    x = _mm512_maskz_loadu_ps(avx512Int2Mask(0xFF00), m1-8);
    x = _mm512_add_ps(x, a.simdInternal_);
    _mm512_mask_storeu_ps(m1-8, avx512Int2Mask(0xFF00), x);
}

static inline void gmx_simdcall
decrHsimd(float *    m,
          SimdFloat  a)
{
    __m512 t;

    assert(std::size_t(m) % 32 == 0);

    a.simdInternal_ = _mm512_add_ps(a.simdInternal_, _mm512_shuffle_f32x4(a.simdInternal_, a.simdInternal_, 0xEE));
    t               = _mm512_maskz_loadu_ps(avx512Int2Mask(0x00FF), m);
    t               = _mm512_sub_ps(t, a.simdInternal_);
    _mm512_mask_storeu_ps(m, avx512Int2Mask(0x00FF), t);
}


template <int align>
static inline void gmx_simdcall
gatherLoadTransposeHsimd(const float *        base0,
                         const float *        base1,
                         const std::int32_t   offset[],
                         SimdFloat *          v0,
                         SimdFloat *          v1)
{
    __m512i idx0, idx1, idx;
    __m512  tmp1, tmp2;

    assert(std::size_t(offset) % 32 == 0);
    assert(std::size_t(base0) % 8 == 0);
    assert(std::size_t(base1) % 8 == 0);
    assert(std::size_t(align) % 2 == 0);

    idx0 = _mm512_maskz_loadu_epi32(avx512Int2Mask(0x00FF), offset);

    idx0 = _mm512_mullo_epi32(idx0, _mm512_set1_epi32(align));
    idx1 = _mm512_add_epi32(idx0, _mm512_set1_epi32(1));

    idx = _mm512_mask_shuffle_i32x4(idx0, avx512Int2Mask(0xFF00), idx1, idx1, 0x44);

    tmp1 = _mm512_i32gather_ps(idx, base0, 4);
    tmp2 = _mm512_i32gather_ps(idx, base1, 4);

    v0->simdInternal_ = _mm512_shuffle_f32x4(tmp1, tmp2, 0x44 );
    v1->simdInternal_ = _mm512_shuffle_f32x4(tmp1, tmp2, 0xEE );
}

static inline float gmx_simdcall
reduceIncr4ReturnSumHsimd(float *     m,
                          SimdFloat   v0,
                          SimdFloat   v1)
{
    __m512 t0, t1;

    assert(std::size_t(m) % 32 == 0);

    /* This is not optimal, but no point optimizing until we know AVX-512 latencies */
    t0 = _mm512_add_ps(v0.simdInternal_, _mm512_permute_ps(v0.simdInternal_, 0x4E));
    t1 = _mm512_add_ps(v1.simdInternal_, _mm512_permute_ps(v1.simdInternal_, 0x4E));
    t0 = _mm512_add_ps(t0, _mm512_permute_ps(t0, 0xB1));
    t0 = _mm512_mask_add_ps(t0, avx512Int2Mask(0xCCCC), t1, _mm512_permute_ps(t1, 0xB1));
    t0 = _mm512_add_ps(t0, _mm512_shuffle_f32x4(t0, t0, 0xB1));
    t0 = _mm512_mask_shuffle_f32x4(t0, avx512Int2Mask(0xAAAA), t0, t0, 0xEE);

    t1 = _mm512_maskz_loadu_ps(avx512Int2Mask(0xF), m);
    t1 = _mm512_add_ps(t1, t0);
    _mm512_mask_storeu_ps(m, avx512Int2Mask(0xF), t1);

    t0 = _mm512_add_ps(t0, _mm512_permute_ps(t0, 0x4E));
    t0 = _mm512_add_ps(t0, _mm512_permute_ps(t0, 0xB1));

    return *reinterpret_cast<float *>(&t0);
}

}      // namespace gmx

#endif // GMX_SIMD_IMPL_X86_AVX_512_UTIL_FLOAT_H
