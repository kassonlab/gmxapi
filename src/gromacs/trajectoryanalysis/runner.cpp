/*
 * This file is part of the GROMACS molecular simulation package.
 *
 * Copyright (c) 2010,2011,2012,2013,2014,2015,2016,2017, by the GROMACS development team, led by
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
/*! \internal \file
 * \brief
 * Defines gmx::trajectoryanalysis::Runner.
 *
 * \ingroup module_trajectoryanalysis
 */

#include "gromacs/trajectoryanalysis/runner.h"

#include "gromacs/trajectoryanalysis/analysismodule.h"
//#include "gromacs/trajectoryanalysis/analysissettings.h"
//#include "gromacs/trajectoryanalysis/runnercommon.h"
//#include "gromacs/selection/selectioncollection.h"

namespace gmx
{
namespace trajectoryanalysis
{

using gmx::TrajectoryAnalysisModule;

Runner::Runner() :
    module_(nullptr),
    settings_(),
    common_(&settings_),
    selections_(),
    pdata_(nullptr),
    nframes_(0),
    is_initialized_(false)
{}

Runner::~Runner()
{}

// The Runner will share ownership of the module argument.
// TODO: clarify requirements and behavior for order of invocation of add_module()
// and initialize()
std::shared_ptr<TrajectoryAnalysisModule> Runner::add_module(std::shared_ptr<TrajectoryAnalysisModule> module)
{
    if (is_initialized_)
    {
        // Alert that we can't add modules anymore.
        return nullptr;
    }
    module_ = module;
    return module_;
}

/// Prepare the runner and modules to start iterating over frames.
/*! Part of initialization is to read the first frame with knowledge of what
 * information is needed by the modules. Thus, modules cannot be added without
 * reinitializing afterwards. For the moment, require forward progress...
 */
void Runner::initialize()
{
    common_.initTopology();
    const TopologyInformation &topology = common_.topologyInformation();
    module_->initAnalysis(settings_, topology);

    // Load first frame.
    common_.initFirstFrame();
    common_.initFrameIndexGroup();
    module_->initAfterFirstFrame(settings_, common_.frame());

    // Nothing seems to use this object and it is only the size of an int, so
    // I don't know why it is passed const ref all over the place...
    AnalysisDataParallelOptions dataOptions;
    pdata_.swap(module_->startFrames(std::move(dataOptions), selections_));

    is_initialized_ = true;
}

bool Runner::next()
{
    if (!is_initialized)
    {
        // Can't run if not initialized...
        // TODO: raise exception.
        return false;
    }
    common_.initFrame();

    // Why isn't this const?
    t_trxframe &frame = common_.frame();

    const TopologyInformation &topology = common_.topologyInformation();

    std::unique_ptr<t_pbc> ppbc_();
    if (settings_.hasPBC())
    {
        set_pbc(ppbc_, topology.ePBC(), frame.box);
    }

    // TODO: convert the next two functions not to need non-const pointers to t_pbc
    selections_.evaluate(&frame, ppbc_.get());
    module_->analyzeFrame(nframes_, frame, ppbc_.get(), pdata.get());
    module_->finishFrameSerial(nframes_);

    ++nframes_;

    if (common_.readNextFrame())
    {
        // There are still more input frames
        return true;
    }
    else
    {
        // Note that there are no more frames.
        return false;
    }
}

int run()
{
    while(next())
    {
        // handle error and return 1;
    };
    return 0;
}

} // end namespace trajectoryanalysis
} // end namespace gmx
