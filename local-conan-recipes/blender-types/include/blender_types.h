// SPDX-FileCopyrightText: 2024 Howetuft
//
// SPDX-License-Identifier: Apache-2.0

// Blender types for pyluxcoreforblender.cpp


#pragma once

#define DNA_DEPRECATED_ALLOW

namespace _btypes {
#include "IMB_imbuf_types.hh"
#include "RE_pipeline.h"
#include "mathutils.h"
#include "DNA_meshdata_types.h"
#include "DNA_customdata_types.h"
#include "DNA_mesh_types.h"

typedef struct MLoopTri {
	unsigned int tri[3];
} MLoopTri;

}

namespace luxcore {
namespace blender {

using namespace std;

using Scene = luxcore::Scene;

using MLoopTri = ::_btypes::MLoopTri;
using MLoopCol = ::_btypes::MLoopCol;
using ImBuf = ::_btypes::ImBuf;
using RenderPass = ::_btypes::RenderPass;
using MatrixObject = ::_btypes::MatrixObject;
using CustomData = ::_btypes::CustomData;
using Mesh = ::_btypes::Mesh;


} // namespace blender
} // namespace luxcore
