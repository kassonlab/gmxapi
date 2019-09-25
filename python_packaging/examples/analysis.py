"""
Analysis tool for adaptive msms
"""

import gmxapi as gmx
import pyemma.coor as coor
import pyemma.msm as msm

tol = 0.1


def relative_entropy(P, Q):
    """
    Takes two transition matrices, calculates relative entropy
    """
    return rel_entropy_P_Q


class MSMAnalyzer:
    """
    Builds msm from gmxapi output trajectory
    """

    def __init__(self, topfile, trajectory, P, N):
        # Build markov model with PyEmma
        feat = coor.featurizer(topfile)
        X = coor.load(trajectory, feat)
        Y = coor.tica(X, dim=2).get_output()
        k_means = coor.cluster_kmeans(Y, k=N)
        centroids = get_centroids(k_means)

        M = msm.estimate_markov_model(kmeans.dtrajs, 100)

        # Q = n-1 transition matrix, P = n transition matrix
        Q = P
        self.P = M.get_transition_matrix()  # figure this out
        self._is_converged = relative_entropy(self.P, Q) < tol

    def is_converged(self):
        return self._is_converged

    def transition_matrix(self):
        return self.P


# Project roadmap notes: Reference FR1 in ../roadmap.rst and ../test/test_fr01.py
msm_analyzer = gmx.make_operation(MSMAnalyzer,
                                  input={'topfile': str, 'trajectory': str, 'P': float, 'N': int},
                                  output={'is_converged': bool, 'transition_matrix': gmx.NDArray}
                                  )
