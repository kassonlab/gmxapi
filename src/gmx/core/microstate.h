//
// Created by Eric Irrgang on 8/10/18.
//

#ifndef GMXPY_MICROSTATE_H
#define GMXPY_MICROSTATE_H

#include <memory>
#include "tprfile.h"
#include "mdcheckpoint.h"

namespace gmxpy
{

class Microstate
{};

/*!
 * \brief Get read access to the microstate corresponding to the provided input.
 *
 * When a TPR file and a checkpoint file are provided, the microstate returned is
 * the configuration and simulation state corresponding to the checkpointed frame
 * of the trajectory produced with the TPR file as input.
 *
 * \warning The current implementation does not rigorously check that the state
 * in the checkpoint was actually produced by the TPR input, only that it is
 * not incompatible with the simulation described in the TPR input.
 *
 * \param tprFile Handle to a TPR file object.
 * \param checkpoint Handle to a simulation checkpoint object.
 *
 * \return Ownership of a new handle to the microstate.
 *
 * After the call completes, data has been read and the TprFile and MDCheckpoint
 * are no longer needed by the returned Microstate.
 */
std::unique_ptr<Microstate> readMicrostate(const TprFile& tprFile, const MDCheckpoint& checkpoint);

}

#endif //GMXPY_MICROSTATE_H
