# This file is part of QuTiP: Quantum Toolbox in Python.
#
#    Copyright (c) 2011 and later, Paul D. Nation and Robert J. Johansson.
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are
#    met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of the QuTiP: Quantum Toolbox in Python nor the names
#       of its contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#    PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#    HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#    THEORY OF LIABILITY, WHETHER IN CONTRACT, SThtRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################

import numpy as np
from numpy.testing import assert_, run_module_suite
from qutip.states import basis, ket2dm
from qutip.quantum_info import (rx, ry, rz, phasegate, cnot, swap, iswap,
                                sqrtswap, toffoli, fredkin, gate_expand_3toN)
from qutip.random_objects import rand_ket, rand_herm
from qutip.tensor import tensor


class TestGates:
    """
    A test class for the QuTiP functions for generating quantum gates
    """

    def testSwapGate(self):
        """
        gates: swap gate
        """
        a, b = np.random.rand(), np.random.rand()
        psi1 = (a * basis(2, 0) + b * basis(2, 1)).unit()

        c, d = np.random.rand(), np.random.rand()
        psi2 = (c * basis(2, 0) + b * basis(2, 1)).unit()

        psi_in = tensor(psi1, psi2)
        psi_out = tensor(psi2, psi1)

        psi_res = swap() * psi_in
        assert_((psi_out - psi_res).norm() < 1e-12)

        psi_res = swap() * swap() * psi_in
        assert_((psi_in - psi_res).norm() < 1e-12)

    def testExpandGate1toN(self):
        """
        gates: expand 1 to N
        """
        N = 7

        for g in [rx, ry, rz, phasegate]:

            theta = np.random.rand() * 2 * 3.1415
            a, b = np.random.rand(), np.random.rand()
            psi1 = (basis(2, 0) + b * basis(2, 1)).unit()
            psi2 = g(theta) * psi1

            psi_rand_list = [rand_ket(2) for k in range(N)]

            for m in range(N):

                psi_in = tensor([psi1 if k == m else psi_rand_list[k]
                                 for k in range(N)])
                psi_out = tensor([psi2 if k == m else psi_rand_list[k]
                                  for k in range(N)])

                G = g(theta, N, m)
                psi_res = G * psi_in

                assert_((psi_out - psi_res).norm() < 1e-12)

    def testExpandGate2toNSwap(self):
        """
        gates: expand 2 to N (using swap)
        """

        a, b = np.random.rand(), np.random.rand()
        k1 = (a * basis(2, 0) + b * basis(2, 1)).unit()

        c, d = np.random.rand(), np.random.rand()
        k2 = (c * basis(2, 0) + b * basis(2, 1)).unit()

        N = 6
        kets = [rand_ket(2) for k in range(N)]

        for m in range(N):
            for n in set(range(N)) - {m}:

                psi_in = tensor([k1 if k == m else k2 if k == n else kets[k]
                                 for k in range(N)])
                psi_out = tensor([k2 if k == m else k1 if k == n else kets[k]
                                  for k in range(N)])

                G = swap(N, m, n)

                psi_res = G * psi_in

                assert_((psi_out - G * psi_in).norm() < 1e-12)

    def testExpandGate2toN(self):
        """
        gates: expand 2 to N (using cnot, iswap, sqrtswap)
        """

        a, b = np.random.rand(), np.random.rand()
        k1 = (a * basis(2, 0) + b * basis(2, 1)).unit()

        c, d = np.random.rand(), np.random.rand()
        k2 = (c * basis(2, 0) + d * basis(2, 1)).unit()

        psi_ref_in = tensor(k1, k2)

        N = 6
        psi_rand_list = [rand_ket(2) for k in range(N)]

        for g in [cnot, iswap, sqrtswap]:

            psi_ref_out = g() * psi_ref_in
            rho_ref_out = ket2dm(psi_ref_out)

            for m in range(N):
                for n in set(range(N)) - {m}:

                    psi_list = [psi_rand_list[k] for k in range(N)]
                    psi_list[m] = k1
                    psi_list[n] = k2
                    psi_in = tensor(psi_list)

                    G = g(N, m, n)
                    psi_out = G * psi_in

                    o1 = psi_out.overlap(psi_in)
                    o2 = psi_ref_out.overlap(psi_ref_in)
                    assert_(abs(o1 - o2) < 1e-12)

                    p = [0, 1] if m < n else [1, 0]
                    rho_out = psi_out.ptrace([m, n]).permute(p)

                    assert_((rho_ref_out - rho_out).norm() < 1e-12)

    def testExpandGate3toN(self):
        """
        gates: expand 3 to N (using toffoli, fredkin, and random 3 qubit gate)
        """

        a, b = np.random.rand(), np.random.rand()
        psi1 = (basis(2, 0) + b * basis(2, 1)).unit()

        c, d = np.random.rand(), np.random.rand()
        psi2 = (basis(2, 0) + b * basis(2, 1)).unit()

        e, f = np.random.rand(), np.random.rand()
        psi3 = (basis(2, 0) + b * basis(2, 1)).unit()

        N = 4
        psi_rand_list = [rand_ket(2) for k in range(N)]

        _rand_gate_U = tensor([rand_herm(2, density=1) for k in range(3)])

        def _rand_3qubit_gate(N=None, m=None, n=None, k=None):
            if N is None:
                return _rand_gate_U
            else:
                return gate_expand_3toN(_rand_gate_U, N, m, n, k)

        for g in [fredkin, toffoli, _rand_3qubit_gate]:

            psi_ref_in = tensor(psi1, psi2, psi3)
            psi_ref_out = g() * psi_ref_in

            for m in range(N):
                for n in set(range(N)) - {m}:
                    for k in set(range(N)) - {m, n}:

                        psi_list = [psi_rand_list[p] for p in range(N)]
                        psi_list[m] = psi1
                        psi_list[n] = psi2
                        psi_list[k] = psi3
                        psi_in = tensor(psi_list)

                        G = g(N, m, n, k)
                        psi_out = G * psi_in

                        o1 = psi_out.overlap(psi_in)
                        o2 = psi_ref_out.overlap(psi_ref_in)
                        assert_(abs(o1 - o2) < 1e-12)


if __name__ == "__main__":
    run_module_suite()
