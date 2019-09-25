/*! \file
 * \brief Provide wrappers for GROMACS restraint compatibility.
 *
 * \todo This should be part of a template library installed with GROMACS.
 *
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#ifndef GMXAPI_PLUGIN_RESTRAINT_H
#define GMXAPI_PLUGIN_RESTRAINT_H

#include <vector>
#include <array>
#include <mutex>
#include "gmxapi/gromacsfwd.h"
#include "gmxapi/session.h"
#include "gmxapi/md/mdmodule.h"
#include "gromacs/restraint/restraintpotential.h"
#include "sessionresources.h"

namespace plugin
{
/*!
 * \brief Wrap a restraint potential implementation.
 *
 * Implement gmx::IRestraintPotential for a restraint potential PotentialT,
 * which defines its input parameter structure as member type `input_param_type`,
 * and which implements calculate() and update() member functions.
 *
 * \tparam PotentialT implementation class
 *
 */
template <class PotentialT>
class Restraint : public gmx::IRestraintPotential, private PotentialT
{
public:
    using typename PotentialT::input_param_type;

    Restraint(std::vector<int> sites, const input_param_type &params,
              std::shared_ptr<plugin::Resources> resources)
        : PotentialT(params), sites_{ std::move(sites) }, resources_{ std::move(resources) }
    {
    }

    ~Restraint() override = default;

    /*!
     * \brief Implement required interface of gmx::IRestraintPotential
     *
     * \return list of configured site indices.
     *
     * \todo remove to template header
     * \todo abstraction of site references
     */
    std::vector<int> sites() const override { return sites_; }

    /*!
     * \brief Implement the interface gmx::IRestraintPotential
     *
     * Dispatch to calculate() method.
     *
     * \param r1 coordinate of first site
     * \param r2 reference coordinate (second site)
     * \param t simulation time
     * \return calculated force and energy
     *
     * \todo remove to template header.
     */
    gmx::PotentialPointData evaluate(gmx::Vector r1, gmx::Vector r2, double t) override
    {
        return PotentialT::calculate(r1, r2, t);
    };

    /*!
     * \brief An update function to be called on the simulation master rank/thread periodically by the Restraint framework.
     *
     * Implements optional override of gmx::IRestraintPotential::update
     *
     * This boilerplate will disappear into the Restraint template in an upcoming gmxapi release.
     */
    void update(gmx::Vector v, gmx::Vector v0, double t) override
    {
        // Todo: use a callback period to mostly bypass this and avoid excessive mutex locking.
        PotentialT::callback(v, v0, t, *resources_);
    };

    /*!
     * \brief Implement the binding protocol that allows access to Session resources.
     *
     * The client receives a non-owning pointer to the session and cannot extent the life of the session. In
     * the future we can use a more formal handle mechanism.
     *
     * \param session pointer to the current session
     */
    void bindSession(gmxapi::SessionResources *session) override
    {
        resources_->setSession(session);
    }

    void setResources(std::unique_ptr<plugin::Resources> &&resources)
    {
        resources_ = std::move(resources);
    }

private:
    std::vector<int>                   sites_;
    std::shared_ptr<plugin::Resources> resources_;
};

} // end namespace plugin

#endif // GMXAPI_PLUGIN_RESTRAINT_H
